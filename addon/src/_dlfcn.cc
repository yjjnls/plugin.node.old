#include <stdio.h>
#include <string>

#ifdef _WIN32
#include <windows.h>
#include <strsafe.h>

#else
#include <dlfcn.h>
#include <unistd.h>
#endif

#ifdef _WIN32

std::string _GetLastError()
{
	LPVOID lpMsgBuf;
	DWORD dw = GetLastError();

	FormatMessageA(
		FORMAT_MESSAGE_ALLOCATE_BUFFER |
		FORMAT_MESSAGE_FROM_SYSTEM |
		FORMAT_MESSAGE_IGNORE_INSERTS,
		NULL,
		dw,
		MAKELANGID(LANG_ENGLISH, SUBLANG_DEFAULT),
		(LPTSTR)&lpMsgBuf,
		0, NULL);
	std::string err((char*)lpMsgBuf);

	LocalFree(lpMsgBuf);
	return err;

}
#endif

int  _chdir(const char *dir)
{
#ifdef _WIN32
	return 0 != ::SetCurrentDirectoryA(dir);
#else
	return 0 == ::chdir(dir);
#endif
}

int _getcwd(char* buf, size_t size)
{
#ifdef _WIN32
	::GetCurrentDirectoryA(size, buf);
#else
	getcwd(buf, size);
#endif	
	return 0;
}

void* _dlopen(const char *filename)
{
#ifdef _WIN32
	return (void*) LoadLibrary(filename);
#else
	return dlopen(filename, RTLD_NOW|RTLD_GLOBAL|RTLD_DEEPBIND);
#endif
}

std::string _dlerror(void)
{
#ifdef _WIN32
	return _GetLastError();
#else
	return dlerror();
#endif

}


void* _dlsym(void *handle, const char *symbol)
{
#ifdef _WIN32
	return GetProcAddress((HINSTANCE)handle, symbol);
#else
	return dlsym(handle, symbol);
#endif
	
}

void _dlclose(void *handle)
{
#ifdef _WIN32
	::FreeLibrary((HINSTANCE)handle);
#else
	dlerror();
#endif
	
}