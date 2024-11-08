from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.node import Host
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time

class MultiConnectionTopology(Topo):
    def build(self):
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
        
        for i in range(10):
            host = self.addHost(f'h{i+1}', cls=Host, defaultRoute=None)
            self.addLink(host, s1, cls=TCLink, bw=10, delay='10ms')

def run_test():
    # 토폴로지 초기화 및 네트워크 시작
    topo = MultiConnectionTopology()
    net = Mininet(topo=topo, autoSetMacs=True, build=False, ipBase="10.0.0.0/24")
    net.start()

    # 각 호스트에 IP 할당
    for i in range(10):
        host = net.getNodeByName(f'h{i+1}')
        host.setIP(intf=f'h{i+1}-eth0', ip=f"10.0.0.{i+1}/24")

    # 임의의 두 호스트(h1, h2) 간 iperf 테스트 실행
    h1 = net.getNodeByName('h1')
    h2 = net.getNodeByName('h2')

    # iperf 서버 시작 (h1에서)
    info("Starting iperf server on h1\n")
    h1.cmd('iperf3 -s &')
    time.sleep(1)  # 서버가 실행될 시간을 잠시 대기

    # 각 호스트에서 iperf 클라이언트 시작 (h2~h10에서 h1로 테스트)
    for i in range(2, 11):
        host = net.getNodeByName(f'h{i}')
        info(f"Starting iperf client on h{i} to h1\n")
        host.cmd(f'iperf3 -c 10.0.0.1 -t 10 &')
        time.sleep(0.5)  # 클라이언트 간의 테스트 시작 시간 간격을 두기

    # CLI 대화형 모드로 네트워크 유지
    CLI(net)

    # 네트워크 종료
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_test()