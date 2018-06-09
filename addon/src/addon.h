#ifndef _NODE_PLUGIN_ADDON_H_
#define _NODE_PLUGIN_ADDON_H_

#include <node_api.h>
#include <uv.h>
#include <map>
#include <list>
#include <string>
#include <assert.h>
#include <stdio.h>

#include "plugin_interface.h"
class Addon;

struct async_callback_t //: public async_callback_param_t 
{
	async_callback_t(const Addon* p, napi_ref cb_ref = nullptr)
		:addon(p), ref(cb_ref),status(0)
	{
		memset(&data, 0, sizeof(data));
	}

	~async_callback_t() {
		if ( data.release) {
			data.release(&data);
		}
	}
	const Addon*     addon;
	napi_ref         ref;
	int              status;

	plugin_buffer_t  data;


};


struct async_notification_t
{
	async_notification_t(plugin_buffer_t* d, plugin_buffer_t* m)
		
	{
		memset(&data, 0, sizeof(data));
		memset(&meta, 0, sizeof(meta));
		if (d) {
			plugin_buffer_safe_move(d, &data);
		}
		if (m) {
			plugin_buffer_safe_move(m, &meta);
		}
	}
	plugin_buffer_t data;
	plugin_buffer_t meta;


	virtual ~async_notification_t() {
		if (data.release) {
			data.release(&data);
		}
		if (meta.release) {
			meta.release(&meta);
		}

	}

};

class Addon {
	enum state_t {
		IDLE = 0,
		INIT,//initializing
		RUN,//running
		TERM    //terminating
	};


public:

	/**************************************/
	/*            NAPI                    */ 
	/**************************************/
	static napi_value Init(napi_env env, napi_value exports);
	static void Destructor(napi_env env, void* nativeObject, void* finalize_hint);
private:
	static napi_value New(napi_env env, napi_callback_info info);
	static napi_value Initialize(napi_env env, napi_callback_info info);
	static napi_value Call(napi_env env, napi_callback_info info);
	static napi_value Release(napi_env env, napi_callback_info info);

	static napi_value Setup(napi_env env, napi_callback_info info);
	static napi_value Teardown(napi_env env, napi_callback_info info);

	static napi_value GetValue(napi_env env, napi_callback_info info);
	static napi_value GetError(napi_env env, napi_callback_info info);
	static napi_ref constructor;

	struct lib_t {
		lib_t() : handle(NULL),create(NULL),destroy(NULL)
		{}
		void* handle;
		plugin_interface_initialize_fn create;
		plugin_interface_terminate_fn  destroy;
	};
private:
	explicit Addon(napi_env env,const std::string& name, const std::string& dir, napi_value* notify = NULL);
	~Addon();

	static void       OnEvent(uv_async_t* handle);

	//void async_call(napi_env env, napi_callback_info info);
	//
	static void plugin_notify(const void* self,
		plugin_buffer_t*    data,
		plugin_buffer_t*    meta)
	{
		plugin_interface_t* iface = (plugin_interface_t*)self;
		Addon* addon = static_cast<Addon*>((void*)iface->context);
		addon->Notify(data, meta);

	}
	void Notify(plugin_buffer_t* data, plugin_buffer_t* meta);


	static void initialize_callback(const void* self,
		const void* context, int status, plugin_buffer_t*    data);

	bool Initialize(napi_value data, napi_value callback);

	static void terminate_callback(const void* self,
		const void* context, int status, plugin_buffer_t*    data);

	bool Terminate( napi_value callback);

	static void callback(const void* self,
		const void* context, int status, plugin_buffer_t* data);

	void Call(napi_value* args);

	void Push(async_callback_t* ac);
	void OnEvent();
	
	bool Setup();
	void Teardown();

	const std::string error() const { return error_; }
	void ExecCallback(async_callback_t* ac, napi_value global);
	void ExecNotification(async_notification_t* ntf, napi_value global);

	//void Release(napi_value callback);
	//void Terminate();
	//void Initial();
	//
	//
	//
	//static void init_done(const void* self, int status, char *msg);
	//static void terminate_done(const void* self, int status, char *msg);
	napi_env env_;
	napi_ref wrapper_;

	uv_mutex_t      mutext_;
	uv_async_t      async_;
	std::list<async_callback_t*>       callbacks_;
	std::list<async_notification_t*>  notifications_;
	std::string error_;
	std::string basename_; //filenmae of the plugin
	std::string directory_; //directory of the plugin 
	//void*       handle_;//dynamic lib handle

	napi_ref           notifier_ref_;
	//plugin_notify_fn   notify_;




	//napi_ref   initial_ref_;
	//napi_ref   terminater_ref_;

	
	state_t state_;
	//bool    plugin_terminated_;
	//bool    plugin_inited_;
	//int status_;
	//std::string msg_;
	std::string version_;

	lib_t   lib_;
	plugin_interface_t* plugin_;

	//bool                running_;
};

#ifndef __NODE_PLUGIN_ADDON_VERSION__
#define __NODE_PLUGIN_ADDON_VERSION__ "0.2.0"
#endif

#endif