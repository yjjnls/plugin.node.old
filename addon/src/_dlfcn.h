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

#ifndef _NODEPLUGIN_DYNAMIC_LIB_WRAP_H_
#define _NODEPLUGIN_DYNAMIC_LIB_WRAP_H_
#include <string>
void *_dlopen(const char *filename);
std::string _dlerror(void);
void *_dlsym(void *handle, const char *symbol);
void _dlclose(void *handle);
int _chdir(const char *dir);
int _getcwd(char *buf, size_t size);

#endif
