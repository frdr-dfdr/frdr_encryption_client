'use strict';

exports.default = async function(configuration) {

    if(configuration.path){
    
      require("child_process").execSync(
     
        `smctl sign --keypair-alias=key_1234567 --input "${String(configuration.path)}"`

      );
    }
};