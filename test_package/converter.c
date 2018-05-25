#include "../addon/src/plugin_interface.h"
#include <ctype.h>
#include <stdio.h>

typedef struct statistic_t {
	int upper;
	int lower;
	int illegal;
}statistic_t;
#define THIS_INSTANCE( p ) ((plugin_interface_t*) p->instance)




int convert(plugin_interface_t* iface, 
	        plugin_buffer_t* data,
			plugin_buffer_t* meta,
			plugin_buffer_t* result);

#define VERSION "0.1.1"
///////////////////////////////////////////////////////////////
static void init (const plugin_interface_t* self,
	              const void*               context,
	              const plugin_buffer_t*    data,
	              plugin_callback_fn        callback)
{
	if (data) {
	}
	plugin_interface_t* iface = (plugin_interface_t*)self;
	iface->instance = malloc(sizeof(statistic_t));
	memset(iface->instance, 0, sizeof(statistic_t));
    if (callback){
		callback(self, context, 0, NULL);
    }
}

//static void _release(plugin_buffer_t* self) {
//	if (self->data) {
//		free( self->data);
//		self->data = NULL;
//	}
//	free( self);
//}


static void call(const plugin_interface_t* self,
	             const void*               context,
	             plugin_buffer_t*          data,
	             plugin_buffer_t*          meta,
	             plugin_callback_fn        callback)
{
	plugin_buffer_t result;
	int status = convert((plugin_interface_t*) self,data, meta, &result);
	callback(self, context, status, &result);
	
	if (!self->notify) return;

	char msg[256];
	plugin_buffer_t m, d;
	statistic_t* s = (statistic_t*)THIS_INSTANCE(self);
	if (status == 0 && self->notify ) {
		sprintf(msg,"{ \"upper\":%d,\"lower\":%d}", s->upper, s->lower);
		plugin_buffer_string_set(&d, msg);
		plugin_buffer_string_set(&m, "success");
	}
	else {
		sprintf(msg, "{ \"illegal\":%d}", s->illegal);
		plugin_buffer_string_set(&d, msg);
		plugin_buffer_string_set(&m, "illegal");

	}
	
	self->notify(self, &d, &m);


	return;
}

static void terminate(const plugin_interface_t* self,
	                  const void*               context,
	                  plugin_callback_fn        callback)
{

    if (callback)
    {
		callback(self,context, 0, NULL);
    }
	if (self->instance) {
		free(self->instance);

		plugin_interface_t* iface = (plugin_interface_t*)self;
		iface->instance = NULL;
	}
}

PLUGIN_INTERFACE(VERSION, init, call, terminate);




static int convert(plugin_interface_t* iface,
	plugin_buffer_t* data,
	plugin_buffer_t* meta,
	plugin_buffer_t* result)
{
	if (!data) {
		plugin_buffer_string_set(result, "string is null.");
		return 1;
	}

	if (!meta) {
		plugin_buffer_string_set(result, "action is null.");
		return 1;
	}

	const char* action = (const char*)meta->data;
	size_t size = meta->size;

	plugin_buffer_safe_move(data, result);
	char* txt = (char*)result->data;
	statistic_t* ps = (statistic_t*)iface->instance;
	if (!strncmp(action, "upper", size))
	{
		for (int i = 0; i < result->size; i++)
		{
			txt[i]=(char)toupper(txt[i]);
		}
		ps->upper++;
	}
	else if (!strncmp(action, "lower", size))
	{
		for (int i = 0; i < result->size; i++)
		{
			txt[i] = (char)tolower(txt[i]);
		}
		ps->lower++;
	}
	else {
		plugin_buffer_string_set(result, "action not support.");
		ps->illegal++;
		return 1;

	}

	return 0;
}