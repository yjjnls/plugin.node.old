
#include "_dlfcn.h"
#include "addon.h"


#define BUFFER_SAFE_RELEASE( buf ) \
if( buf.release ){                 \
   buf.release(&buf);              \
}






Addon::Addon(napi_env env,const std::string& name,const std::string& dir, napi_value* notify)
	: env_(env), wrapper_(nullptr)
	, plugin_(nullptr)
	, notifier_ref_(nullptr)
	, state_(Addon::IDLE)
	, basename_(name)
	, directory_(dir)
{
	uv_async_init(uv_default_loop(), &async_, Addon::OnEvent);
	async_.data = this;

	uv_mutex_init(&mutext_);
	if (notify)
	{
		napi_create_reference(env_, *notify, 1, &notifier_ref_);
	}


}

Addon::~Addon()
{
	napi_delete_reference(env_, wrapper_);
}


void Addon::initialize_callback(const void* self,
	const void* context, int status,
	plugin_buffer_t*    data)
{
	async_callback_t* ac = (async_callback_t*)context;
	assert(ac);
	Addon* addon = (Addon*)ac->addon;
	ac->status = status;
	plugin_buffer_safe_move(data, &ac->data);

	addon->Push(ac);
}


bool Addon::Initialize(napi_value data, napi_value callback)
{
	plugin_ = lib_.create(this, this->notifier_ref_ ? Addon::plugin_notify: NULL);
	if (!plugin_) {
		napi_throw_error(env_, "127", "create plugin inteface failed.");
		return false;
	}
	
	napi_valuetype valuetype;
	napi_status status;
	
	plugin_notify_fn notify = NULL;
	if (this->notifier_ref_) {
		plugin_->notify = Addon::plugin_notify;
	}
	status = napi_typeof(env_, callback, &valuetype);
	assert(status == napi_ok);
	napi_ref ref = nullptr;
	if (valuetype == napi_function)
	{
		status = napi_create_reference(env_, callback, 1, &ref);
		assert(status == napi_ok);
	}

	async_callback_t* ac = new async_callback_t(this, ref);
	
	status = napi_typeof(env_, data, &valuetype);
	assert(status == napi_ok);

	bool is_buffer;
	status = napi_is_buffer(env_, data, &is_buffer);
	assert(status == napi_ok);

	if (!is_buffer)
	{
		plugin_->init(plugin_, ac, NULL, Addon::initialize_callback);
	}
	else
	{
		plugin_buffer_t buffer;
		memset(&buffer, 0, sizeof(buffer));
		status = napi_get_buffer_info(env_, data, &buffer.data, &buffer.size);
		assert(status == napi_ok);

		plugin_->init(plugin_, ac, &buffer, Addon::initialize_callback);
	}

	state_ = Addon::INIT;
	return true;

}


//
// utils
//

bool Addon::Setup()
{
	char _CWD[FILENAME_MAX] = { 0 };
	void* handle = NULL;

	_getcwd(_CWD, sizeof(_CWD));

	if (!directory_.empty())
	{
		
		if (!_chdir(directory_.c_str())) {
			error_ = "can not switch <" + directory_ + "> to load plugin.";
			return false;
		}

	}
	std::string path = std::string(_CWD) + "/" + basename_;

	handle = _dlopen(basename_.c_str());

	if (!directory_.empty())
	{
		if (!_chdir(_CWD)) {
			error_ = "can not recover to original work directory:" + std::string(_CWD);
			return false;
		}
	}

	if (!handle)
	{
		error_ = path + " : " +_dlerror();
		return false;
	}
	lib_.handle = handle;

	lib_.create = (plugin_interface_initialize_fn)_dlsym(handle, "plugin_interface_initialize");
	if (!lib_.create)
	{
		error_ = "invalid plugin, no <plugin_interface_initialize>";
		_dlclose(lib_.handle);
		lib_.handle = NULL;
		return false;
	}
	
	lib_.destroy =
		(plugin_interface_terminate_fn)_dlsym(handle, "plugin_interface_terminate");
	
	if (!lib_.destroy)
	{
		error_ = "invalid plugin, no <plugin_interface_terminate>";
		_dlclose(lib_.handle);
		lib_.handle = NULL;
		lib_.create = NULL;
		return false;
	}
	return true;
}

void Addon::Teardown()
{
	for (std::list<async_callback_t*>::iterator it = callbacks_.begin();
		it != callbacks_.end(); it++)
	{
		async_callback_t* ac = *it;
		if (ac->ref) {
			napi_delete_reference(env_, ac->ref);
		}
		
		if (ac->data.release) {
			ac->data.release(&ac->data);
		}
		delete *it;
	}
	callbacks_.swap(std::list<async_callback_t*>());

	for (std::list<async_notification_t*>::iterator it = notifications_.begin();
		it != notifications_.end(); it++)
	{
		async_notification_t* n = *it;


		delete *it;
	}
	notifications_.swap(std::list<async_notification_t*>());

	napi_delete_reference(env_, notifier_ref_);
	notifier_ref_ = nullptr;

	if (plugin_) 
	{
		plugin_interface_terminate_fn(plugin_);
		plugin_ = NULL;
	}

	if (lib_.handle) 
	{
		if (lib_.destroy)
		{
			lib_.destroy(plugin_);
		}
		_dlclose(lib_.handle);
		lib_.handle = NULL;
	}

	uv_close((uv_handle_t*)&async_, NULL);

}

void Addon::Notify(plugin_buffer_t* data, plugin_buffer_t* meta)
{
	async_notification_t* ac = new async_notification_t(data, meta);
	uv_mutex_lock(&mutext_);
	notifications_.push_back( ac);
	uv_mutex_unlock(&mutext_);
	uv_async_send(&async_);

}

inline void Addon::ExecCallback(async_callback_t* ac,napi_value global)
{
	plugin_buffer_t& param = ac->data;

	if (ac->ref) {
		napi_value cb;
		napi_status status = napi_get_reference_value(env_, ac->ref, &cb);
		assert(status == napi_ok);

		napi_value argv[2];
		size_t argc = 1;

		status = napi_create_int32(env_, ac->status, &argv[0]);
		if (param.data && param.size)
		{
			napi_create_buffer_copy(env_, param.size, (const void*)param.data, NULL, &argv[1]);
			argc++;
		}

		napi_value result;
		status = napi_call_function(env_, global, cb, argc, argv, &result);
		assert(status == napi_ok);
		napi_delete_reference(env_, ac->ref);
		
	}
	if (param.release) {
		param.release(&param);		
	}
	delete ac;
}

inline void Addon::ExecNotification(async_notification_t* ntf, napi_value global)
{
	if (notifier_ref_ && (ntf->data.data || ntf->meta.data)) {
		napi_value cb=nullptr;
		napi_status status = napi_get_reference_value(env_, notifier_ref_, &cb);
		assert(status == napi_ok);

		napi_value argv[2] = { nullptr,nullptr };
		size_t argc = 2;
		plugin_buffer_t& d = ntf->data;
		plugin_buffer_t& m = ntf->meta;
		if (d.data && d.size) {
			napi_create_buffer_copy(env_, d.size, (const void*)d.data, NULL, &argv[0]);
		}

		if (m.data && d.size) {
			napi_create_buffer_copy(env_, m.size, (const void*)m.data, NULL, &argv[1]);
		}

		napi_value result;
		status = napi_call_function(env_, global, cb, argc, argv, &result);
		assert(status == napi_ok);
	}
	delete ntf;
}
void Addon::OnEvent()
{
	napi_status status;

	std::list<async_callback_t*> cbs;
	std::list<async_notification_t*> ntfs;
	state_t state = IDLE;
	uv_mutex_lock(&mutext_);
	state = state_;
	cbs.swap(callbacks_);
	ntfs.swap(notifications_);
	uv_mutex_unlock(&mutext_);

	napi_handle_scope scope;
	status = napi_open_handle_scope(env_, &scope);

	napi_value global;
	status = napi_get_global(env_, &global);
	assert(status == napi_ok);

	
	//callback
	for (std::list<async_callback_t*>::iterator it = cbs.begin();
		it != cbs.end(); it++)
	{
		this->ExecCallback(*it,global);
	}

	//notify
	for (std::list<async_notification_t*>::iterator it = ntfs.begin();
		it != ntfs.end(); it++) {
		ExecNotification(*it, global);
	}
	napi_close_handle_scope(env_, scope);
}

void Addon::terminate_callback(const void* self,
	const void* context, int status, plugin_buffer_t*    data)
{
	async_callback_t* ac = (async_callback_t*)context;
	assert(ac);
	Addon* addon = (Addon*)ac->addon;
	ac->status = status;

	plugin_buffer_safe_move(data, &ac->data);

	addon->Push(ac);

}


bool Addon::Terminate(napi_value callback)
{
	state_ = Addon::TERM;
	napi_valuetype valuetype;
	napi_status status;
	status = napi_typeof(env_, callback, &valuetype);
	assert(status == napi_ok);
	assert(valuetype == napi_function);

	napi_ref ref = nullptr;
	if (valuetype == napi_function)
	{
		status = napi_create_reference(env_, callback, 1, &ref);
		assert(status == napi_ok);
	}

	async_callback_t* ac = new async_callback_t(this, ref);

	plugin_->terminate(plugin_,ac, Addon::terminate_callback);
	return true;

}

inline void Addon::Push(async_callback_t* ac)
{
	uv_mutex_lock(&mutext_);
	callbacks_.push_back(ac);
	uv_mutex_unlock(&mutext_);
	uv_async_send(&async_);
}

static void  default_release(plugin_buffer_t* self)
{
	if (self == NULL)
	{
		return;
	}

	if (self->data) {
		free(self->data);
	}

	free(self);
	return;
}

void Addon::callback(const void* self,
	const void* context, int status, plugin_buffer_t* data)
{
	async_callback_t* ac = (async_callback_t*)context;
	Addon* addon = (Addon*)ac->addon;
	ac->status = status;
	plugin_buffer_safe_move(data, &ac->data);

	addon->Push(ac);
}

void Addon::Call(napi_value* args)
{
	napi_status status;
	napi_valuetype valuetype;

	plugin_buffer_t* data = NULL;
	plugin_buffer_t* meta = NULL;
	plugin_buffer_t  bufs[2];
	memset(&bufs, 0, sizeof(bufs));

	status = napi_typeof(env_, args[0], &valuetype);
	assert(status == napi_ok);
	if (valuetype == napi_object)
	{
		napi_get_buffer_info(env_, args[0], &bufs[0].data, &bufs[0].size);
		data = &bufs[0];
	}

	status = napi_typeof(env_, args[1], &valuetype);
	assert(status == napi_ok);
	if (valuetype == napi_object)
	{
		napi_get_buffer_info(env_, args[1], &bufs[1].data, &bufs[1].size);
		meta = &bufs[1];
	}

	napi_ref ref;
	napi_create_reference(env_, args[2], 1, &ref);
	async_callback_t* ac = new async_callback_t(this, ref);
	plugin_->call(plugin_, ac, data, meta, Addon::callback);
}


