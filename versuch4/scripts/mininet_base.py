from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info, lg
from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
from mininet.util import waitListening


from mininet.node import OVSController


class NetTopo(Topo):
    def __init__(self, loss):
        Topo.__init__(self)
        c1 = self.addHost('c1', ip='10.11.0.1/24')
        c2 = self.addHost('c2', ip='10.12.0.2/24')
        sv1 = self.addHost('sv1', ip='10.11.0.3/24')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        self.addLink(c1, s1, bw=1)
        self.addLink(c2, s1, bw=1)
        self.addLink(s1, s2, bw=1, loss=loss)
        self.addLink(sv1, s2, bw=1)
        self.addLink(sv1, s2, bw=1)

        self.addLink(s3, c1)
        self.addLink(s3, c2)
        self.addLink(s3, sv1)

def conf(net):
    net['c1'].cmd('ip addr add 10.0.0.1/24 dev c1-eth1')
    net['c2'].cmd('ip addr add 10.0.0.2/24 dev c2-eth1')
    net['sv1'].cmd('ip addr add 10.0.0.3/24 dev sv1-eth2')

    net['sv1'].cmd('ip addr add 10.12.0.3/24 dev sv1-eth1')

def sshd(net):
    root = Node('root', inNamespace=False)
    intf = net.addLink(root, net['s3']).intf1
    root.setIP('10.0.0.4/24', intf=intf)

    net.start()
    root.cmd('route add -net 10.0.0.0/24 dev ' + str(intf))

    for host in net.hosts:
        host.cmd('/usr/sbin/sshd -D -o UseDNS=no -u0&')

def start(loss):
    lg.setLogLevel('info')
    topo = NetTopo(loss=loss)
    net = Mininet(topo = topo, controller = OVSController)

    conf(net)
    sshd(net)

    CLI(net)
    net.stop()
