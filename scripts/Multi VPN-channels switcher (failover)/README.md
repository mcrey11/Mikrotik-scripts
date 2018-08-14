# Multi VPN-channels switcher (failover)

### 1. Import and set/tune parameters in vpn-tunnel-check and vpn-interfaces scripts:

**vpn-tunnel-check** :

_gw_ – what to ping
_cnt2ping_ – how much too ping
_minlevel_ – minimum allowed successful ping to count channel alive

**vpn-interfaces** :

_imask_ – mask for switched channels. For example “^VPN*” means channels, starting from “VPN” in their name.
_delayBeforeChecks_ – delay between enabling of channel and starting it’s health check.

_checkIfRunning_ – will we check “running” status. Makes sense for pptp/l2tp.
_runningDelay_ – delays between “running” checks
_runningMaxCount_ – how long we will wait for “running”=true

_checkIfPing_ – will we check health of channel by pinging.
_checkPing2Interface_ – will we specify interface during ping. I.e. will we ping via concrete interface.
_ping2host_ – host to be pinged
_pingMaxCount_ – how much to ping
_pingMinCount_ – minimal successful pings to count channel alive

### 2. Check scripts vpn-tunnel-check and vpn-interfaces by running them from terminal.

### 3. Enable vpn-check-task scheduler task.

More information can be read here:</br>
https://www.coders.in.ua/2018/02/13/multi-vpn-channels-switcher-failover/</br>
https://forum.mikrotik.com/viewtopic.php?f=9&t=130773</br>
