
var arguments = process.argv;

PLUGIN_PATH    = arguments[2]
CONVERTER_PATH = arguments[3]
//console.log(arguments)
//console.log(plugin_path)
//console.log(converter_path)
const assert = require('assert');
console.log("****",PLUGIN_PATH)
var node_plugin = require('./plugin.node')
//const path=require('path');
//const util = require('util');
//
///*
//basename_ = path.basename( converter_path)
//dirname_  = path.dirname( converter_path )
//plugin = new node_plugin.Plugin(basename,basename, function( data,meta){
//    console.log( data,meta)
//})
//
//assert( plugin.setup() )
//*/
//
//class Converter {
//    constructor(notify) {
//        
//        this.upper  = 0
//        this.lower  = 0
//        this.illegal= 0
//
//        this.plugin_ = new node_plugin.Plugin(
//            path.basename( CONVERTER_PATH),
//            path.dirname( CONVERTER_PATH ), 
//            (data,meta)=>{this.notification(data,meta)})        
//    }
//
//    initialize(){
//        assert( this.plugin_.setup() )
//        assert( this.plugin_.initialize(option) );
//    }
//
//    terminate(){
//        return this.plugin_.terminate()
//    }
//
//    convert(action,text){
//        let self = this
//        return new Promise(function (resolve, reject) {
//            var meta = Buffer.from(action,'utf8')
//            var data = Buffer.from(text,'utf8')
//            self.plugin_.call(data,meta ).then(
//                (res)=>{
//                    var value = res.toString('utf8')
//                    resolve(value);
//                }
//            ).catch( (err)=>{
//                var msg = err.toString()
//                reject(msg);
//            })
//		})
//    }
//
//    notification(data,meta){
//        var type = meta.toString('utf8');
//        var j={}
//        if( data ){
//            j = JSON.parse(data.toString('utf8'));
//        }
//
//        if( type == 'success'  ){
//            this.upper = j.upper
//            this.lower = j.lower
//        } else if( type == 'illegal'){
//            this.illegal = j.illegal;
//        }
//    }
//    
//}
//
//
//converter = Converter()
//converter.initialize()