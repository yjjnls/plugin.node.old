/*
 * Copyright 2018 KEDACOM Inc. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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
        0,
        NULL);
    std::string err((char *)lpMsgBuf);

    LocalFree(lpMsgBuf);
    return err;
}
#endif

int _chdir(const char *dir)
{
#ifdef _WIN32
    return 0 != ::SetCurrentDirectoryA(dir);
#else
    return 0 == ::chdir(dir);
#endif
}

int _getcwd(char *buf, size_t size)
{
#ifdef _WIN32
    ::GetCurrentDirectoryA(size, buf);
#else
    getcwd(buf, size);
#endif
    return 0;
}

void *_dlopen(const char *filename)
{
#ifdef _WIN32
    return (void *)LoadLibrary(filename);
#else
    return dlopen(filename, RTLD_NOW | RTLD_GLOBAL | RTLD_DEEPBIND);
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


void *_dlsym(void *handle, const char *symbol)
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
