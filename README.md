| Bintray | Windows | Linux  |
|:--------:|:---------:|:-----------------:|
|[![Download](https://api.bintray.com/packages/pluginx/testing/plugin.node:pluginx/images/download.svg)](https://bintray.com/pluginx/testing/plugin.node:pluginx/_latestVersion)[![Download](https://api.bintray.com/packages/pluginx/stable/plugin.node:pluginx/images/download.svg)](https://bintray.com/pluginx/stable/plugin.node:pluginx/_latestVersion)|[![Build status](https://ci.appveyor.com/api/projects/status/github/Mingyiz/plugin.node?svg=true)](https://ci.appveyor.com/project/Mingyiz/plugin-node)|[![](https://www.travis-ci.org/yjjnls/plugin.node.svg?branch=master)](https://github.com/yjjnls/plugin.node)


# How to build
This project use conan as build tools, so you can read [conan docs](https://docs.conan.io/en/latest/).

or, you can use more easy way
Python >=2.7  and Node >=10 is required


```shell
  pip install conan --upgrade
  pip install conan_package_tools bincrafters_package_tools
  pip install shell
  npm install node-gyp -g
  node-gyp install
  
  ...  set enviroment here ...

  python setup.py
```

  




