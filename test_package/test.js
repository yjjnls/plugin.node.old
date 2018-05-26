
var arguments = process.argv;

PLUGIN_PATH    = arguments[2]
CONVERTER_PATH = arguments[3]

console.log(`
node.js: ${process.version}
platform: ${process.platform}
arch: ${process.arch}
plugin.node: ${PLUGIN_PATH}
plugin: ${CONVERTER_PATH}
`)
const path   = require('path')
const assert = require('assert');
var node_plugin = require(PLUGIN_PATH)
    
function test(action,text, done, fail){

    
    var plugin = new node_plugin.Plugin(
        path.basename( CONVERTER_PATH),
        path.dirname( CONVERTER_PATH ), 
        (data,meta)=>{
            
        });

    if (!plugin.setup()){
        fail("setup failed.");
        return;
    };

    function terminate(){
        plugin.release( (status,res) => {
            setTimeout(function() {
                plugin.teardown()
            }, 0);
        })
    }

    
	plugin.initialize("", (status,res) => {
        if( status != 0 ){
            terminate()
            fail("init failed.");
            return
        }

        var meta = Buffer.from(action,'utf8')
        var data = Buffer.from(text,'utf8')
        plugin.call(data,meta  ,(status,res)=>{
            terminate()
            if( status != 0 ){                
                fail("init failed.");
                return
            }
            done( res.toString('utf8'));    
        })
	})
}
var result = undefined
var error = undefined
test("upper","aAbB",(res)=>{
    if ('AABB' === res){
        console.log("success !")
        process.exit(0)
    } else {
        console.error("converter error !")
        process.exit(2)        
    }

},(err)=>{
    error = err 
    console.error("error:",err);
    process.exit(1)
})





