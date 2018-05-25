#include "addon.h"

#define DECLARE_NAPI_METHOD(name, func)                          \
  { name, 0, func, 0, 0, 0, napi_default, 0 }


napi_ref Addon::constructor;


napi_value Addon::New(napi_env env, napi_callback_info info) {
	napi_status status;

	napi_value target;
	status = napi_get_new_target(env, info, &target);
	assert(status == napi_ok);
	bool is_constructor = target != nullptr;

	if (is_constructor) {
		// Invoked as constructor: `new Addon(...)`
		size_t argc = 3;
		napi_value args[3];
		napi_value jsthis;
		status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);
		assert(status == napi_ok);
		assert(argc == 3);

		napi_valuetype valuetype;
		status = napi_typeof(env, args[0], &valuetype);
		assert(status == napi_ok);
		assert(valuetype == napi_string);
		char path[FILENAME_MAX];
		size_t len;
		status = napi_get_value_string_utf8(env, args[0], path, FILENAME_MAX, &len);
		assert(status == napi_ok);
		std::string name(path);

		status = napi_typeof(env, args[1], &valuetype);
		assert(status == napi_ok);
		assert(valuetype == napi_string);

		status = napi_get_value_string_utf8(env, args[1], path, FILENAME_MAX, &len);
		assert(status == napi_ok);
		std::string dir(path);

		napi_value* notify = NULL;
		status = napi_typeof(env, args[2], &valuetype);
		assert(status == napi_ok);
		if (valuetype == napi_function)
		{
			notify = &args[2];
		}


		Addon* obj = new Addon(env,name, dir,notify);

		status = napi_wrap(env,
			jsthis,
			reinterpret_cast<void*>(obj),
			Addon::Destructor,
			nullptr,  // finalize_hint
			&obj->wrapper_);
		assert(status == napi_ok);

		return jsthis;
	}
	else {
		// Invoked as plain function `Addon(...)`, turn into construct call.
		size_t argc_ = 1;
		napi_value args[1];
		status = napi_get_cb_info(env, info, &argc_, args, nullptr, nullptr);
		assert(status == napi_ok);

		const size_t argc = 1;
		napi_value argv[argc] = { args[0] };

		napi_value cons;
		status = napi_get_reference_value(env, constructor, &cons);
		assert(status == napi_ok);

		napi_value instance;
		status = napi_new_instance(env, cons, argc, argv, &instance);
		assert(status == napi_ok);

		return instance;
	}
}


napi_value Addon::Setup(napi_env env, napi_callback_info info)
{
	size_t argc = 2;
	napi_value args[2];
	napi_value jsthis;
	napi_status status;
	status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);

	Addon* obj;
	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
	bool result = obj->Setup();
	napi_value value;
	napi_get_boolean(env, result, &value);
	return value;

}
napi_value Addon::Teardown(napi_env env, napi_callback_info info)
{
	size_t argc = 2;
	napi_value args[2];
	napi_value jsthis;
	napi_status status;
	status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);

	Addon* obj;
	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
	obj->Teardown();
	return nullptr;
}

// =>( data, callback )
napi_value Addon::Initialize(napi_env env, napi_callback_info info) {
	napi_status status;

	size_t argc = 2;
	napi_value args[2];
	napi_value jsthis;
	status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);
	assert(status == napi_ok);
	assert(argc == 2);

	napi_valuetype valuetype;
	status = napi_typeof(env, args[0], &valuetype);
	assert(status == napi_ok);

	status = napi_typeof(env, args[1], &valuetype);
	assert(status == napi_ok);
	assert(valuetype == napi_function);


	Addon* obj;
	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));

	obj->Initialize(args[0], args[1]);

	return nullptr;
}
napi_value Addon::Release(napi_env env, napi_callback_info info)
{
	Addon* obj;
	size_t argc = 3;
	napi_value args[3];
	napi_value jsthis;
	napi_status status;
	status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);
	assert(status == napi_ok);

	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
	assert(status == napi_ok);
	obj->Terminate(args[0]);
	return nullptr;
}

napi_value Addon::Call(napi_env env, napi_callback_info info)
{
	napi_status status;
	void   *data = NULL, *meta = NULL;
	size_t len = 0, mlen = 0;


	size_t argc = 3;
	napi_value args[3];
	napi_value jsthis;
	status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);
	assert(status == napi_ok);
	assert(argc == 3);


	Addon* obj;
	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
	assert(status == napi_ok);
	obj->Call(args);

	return nullptr;
}

void Addon::Destructor(napi_env env, void* nativeObject, void* /*finalize_hint*/) {
	reinterpret_cast<Addon*>(nativeObject)->~Addon();
}


void Addon::OnEvent(uv_async_t* handle)
{
	Addon* obj = (Addon*)handle->data;
	obj->OnEvent();
}


napi_value Addon::GetValue(napi_env env, napi_callback_info info) {
	napi_status status;

	napi_value jsthis;
	status = napi_get_cb_info(env, info, nullptr, nullptr, &jsthis, nullptr);
	assert(status == napi_ok);

	Addon* obj;
	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
	assert(status == napi_ok);

	napi_value ver;
	
	status = napi_create_string_utf8(env, __NODE_PLUGIN_ADDON_VERSION__, strlen(__NODE_PLUGIN_ADDON_VERSION__), &ver);
	
	assert(status == napi_ok);

	return ver;
}


napi_value Addon::GetError(napi_env env, napi_callback_info info) 
{
	napi_status status;

	napi_value jsthis;
	status = napi_get_cb_info(env, info, nullptr, nullptr, &jsthis, nullptr);
	assert(status == napi_ok);

	Addon* obj;
	status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
	assert(status == napi_ok);

	napi_value err;

	status = napi_create_string_utf8(env, obj->error().c_str(), obj->error().size()+1, &err);

	assert(status == napi_ok);

	return err;
}

napi_value Addon::Init(napi_env env, napi_value exports) {
	napi_status status;
	napi_property_descriptor properties[] = {
	DECLARE_NAPI_METHOD("setup", Setup),
	DECLARE_NAPI_METHOD("teardown", Teardown),

	DECLARE_NAPI_METHOD("initialize", Initialize),
	DECLARE_NAPI_METHOD("call", Call),
	DECLARE_NAPI_METHOD("release", Release),

	{"error"  , 0, 0, GetError, 0, 0, napi_default, 0 },
	{"version", 0, 0, GetValue, 0, 0, napi_default, 0}
	};
	napi_value cons;
	status =
		napi_define_class(env, "Plugin", NAPI_AUTO_LENGTH, New, nullptr, 7, properties, &cons);
	assert(status == napi_ok);

	status = napi_create_reference(env, cons, 1, &constructor);
	assert(status == napi_ok);

	status = napi_set_named_property(env, exports, "Plugin", cons);
	assert(status == napi_ok);
	return exports;
}



/****************************************/
napi_value Init(napi_env env, napi_value exports) {
	return Addon::Init(env, exports);
}

NAPI_MODULE(node_plugin, Init)