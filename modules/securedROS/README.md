# secure ROS API (under development)

ROS API wrapper with some security added (in future)

## Features
- [x] router device can be pre-configued - config/credentials stored separatly and can be accessed from client's code
- [x] API wrapped in black-box style - i.e. inside client's code you can just receive context of desired router 
      and do only listed for this router actions i.e. no full control on router given. 
      ROS have rediculus persmissions controls for router users.  

## Configuration / Installation
1. Router:
- enable _api-ssl_
- enable 8729 (or another) port only for specific peers via firewall
- add _Available From_ in api-ssl config
- use router certificate
- create own _ro_ and _rw_ users for api and restrict access for specific API


###Installation:                                        
   Run:
   ```bash
   cd ~
   ```
   Edit config files and run script (see log of install.sh for details)

 
 
### Settings

### Debug

---

### Known issues

#### 

