# OpenVPN server with client certificates helper scripts

## 1. Install
### Copy to router certs.rsc and import it:
   ```bash
   /import "certs.rsc"
   ```
   After successful import you will see 4 scripts in _System_->_Scripts_:
    **certs_defaults** - defaults for all scripts
    **certs_createCA** - generate CA certificate
    **certs_createServer** - create server's certificate
    **certs_createClient** - create client's certificate

### Set defaults in 
