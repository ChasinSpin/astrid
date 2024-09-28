# Wi-Fi

**Per person support for WiFi networks is not provided. Common problems are misconfigured networks, routers and misunderstanding of how networking works. Compounding the issue is that network settings can't be changed over a zoom session without killing the zoom session, making it difficult or impossible for someone remote to assist.**

**If you are having issues connecting to your home network, it is recommended that you find someone local who understands networking technology and can assist you.**

The following is a list of things we have encountered and should be worked through systematically if you are having difficulty connecting Astrid to the Internet.

* Mesh networks: These can cause issues with Astrid and other devices. Mesh networks often disconnect a device and expect it to reconnect, either between 2GHz and 5GHz or to other nodes in the mesh, as signal strength changes. It is strongly recommended to turn this auto-switching off.  Also, mesh implementations and reliability can vary between vendors.  I used to have a Linksys mesh that was highly unreliable, and now I've switched to a TP-Link, which is reliable (for the most part) for example.

* Wi-Fi Extenders: These can be unreliable, depending on vendor.

* Different Network Frequencies with the same name: If you have a 2GHz and 5GHz network with the same name, it's unclear which one Astrid is connecting to.

* 2GHz has more range than 5GHz: Use 2GHz

* Signal strength: Astrid is built on a Raspberry Pi which has a small Wi-Fi antenna due to space constraints.  You should expect it to have 1/3 to 1/2 the range of a typical large laptop or desktop.

* Wi-Fi signal not green on Astrid Mini Display: If it's not green, then you don't have a good enough connection, full stop.  Get closer to your router.

* Wrong Password: If you have entered the wrong Wi-Fi password, you can't connect to the Wi-Fi.

* IPs and DNS: The internet works on IP addresses, e.g. 192.168.40.182, that's what you connect to; however, because humans are poor at remembering numbers, there's a service called DNS that maps names to numbers. Astrid advertises its DNS translation via a service called mDNS, which has to be working to be able to connect to Astrid-XXXX.local.  mDNS is handled by your router or the device you are running RealVNC on.  Routers and machines often have broken mDNS implementations.  If mDNS isn't working, then connect to the IP address.

* MacOS: Recent versions of MacOS may disable the ability of RealVNC to connect via the local network, you need to enable the security setting for Lan on your machine.

* Windows: Windows historically had a broken mDNS implementation.  And periodically breaks it again in updates.  Use IP address.

* Old Android Tablets: These have missing mDNS implementations.  Use the IP address.

* Wrong Network: When in Astrid Hotspot mode, then you should connect your Wi-Fi network to Astrid's Hotspot.  When Astrid is connected to your home network, then you should connect your Wi-Fi network to your home network.  If you don't do this, then you won't be able to connect.

* Mini Display: Astrid ALWAYS tells you what it's connected to, whether it's advertising the Hotspot and what the IP addresses and hostname are.  Use these to determine where you should be connecting.

* Poor Signal: Consider purchasing a travel router.

* No Internet: Does the Mini Display say you're connected to your home network?  If it does, do you have an IP?  If you have an IP, are connected and the signal is good, then your router is misconfigured.

* Ethernet: Ethernet is not supported, if you need to use it, see: [Connectivity WiFi and Hotspot](https://github.com/ChasinSpin/astrid/blob/4050e875f35812b1c8385b21fdba735a35613dd9/docs/UsageGuide.md#connectivity-wifi-and-hotspot)