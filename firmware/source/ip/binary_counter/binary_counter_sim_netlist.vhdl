-- Copyright 1986-2019 Xilinx, Inc. All Rights Reserved.
-- --------------------------------------------------------------------------------
-- Tool Version: Vivado v.2019.2 (lin64) Build 2708876 Wed Nov  6 21:39:14 MST 2019
-- Date        : Sun Dec  4 00:05:04 2022
-- Host        : ubuntu running 64-bit Ubuntu 18.04.6 LTS
-- Command     : write_vhdl -force -mode funcsim -rename_top binary_counter -prefix
--               binary_counter_ binary_counter_sim_netlist.vhdl
-- Design      : binary_counter
-- Purpose     : This VHDL netlist is a functional simulation representation of the design and should not be modified or
--               synthesized. This netlist cannot be used for SDF annotated simulation.
-- Device      : xc7a200tsbg484-1
-- --------------------------------------------------------------------------------
`protect begin_protected
`protect version = 1
`protect encrypt_agent = "XILINX"
`protect encrypt_agent_info = "Xilinx Encryption Tool 2019.1"
`protect key_keyowner="Cadence Design Systems.", key_keyname="cds_rsa_key", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=64)
`protect key_block
mCTsLEbsPZ2vQwU8/7gCUSK/pChAk9a06Ca2pzXOPgWuyZNUN2/38IFSH3fobTOXCRoicKPjw/zS
U5JdUhkrLw==

`protect key_keyowner="Synopsys", key_keyname="SNPS-VCS-RSA-2", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`protect key_block
GFPI7s4C1t7CtVyK1SFEMXCUuPDr0XM3dS0SXtjjql05Q6JUKrxMZaM7re8CPIaDa54K1WYrSiji
LOfE418BW3NruEHp6g4ffIGVmqD/6oXHlSP/+pZ+GD8J3ZZ9gHEnk9BLpUeWxtZunteh6jCktwBR
rDRNRE7evKc0RdE4Dzg=

`protect key_keyowner="Aldec", key_keyname="ALDEC15_001", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
sEab41ij0Mmj3TOzy5LUFbrA1DGo6sn7RpcTh4zIXnxchi7xaGXTH4JkUR4ERWmrZubZVNuDty3G
4TW7X1eXkIYL0g3rTl1BN/pYJcBojhcX71F3LLIf2z50xQX6C59oMYwkdcd0PKmDVIlUkuP55LXc
ILCABg2L8H6UmzHAHUiOb/o2/XfUUvzZHBTzPfY1N5j5wGyuLLxHjbTs22mz7su4SFA4cDz1ALYw
WqIXTEkTzRpnoV5wAq1v0Vljr91e3XWzZQtWtVlINSogSOqFkFryC5Sn6XgFKHe60XmBBtCyjXg/
RpESrybcLJXn3Sff/R8O4K5MV88ExUrcKlwcbw==

`protect key_keyowner="ATRENTA", key_keyname="ATR-SG-2015-RSA-3", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
kVMOfbqeAFbRG9AMrD5M+safOIxNtaCf7vbQo4khE4OGfju8gRGpKeH/RBfeF976g2hwQ3yb68+C
IHXa4Ggqv86YT+lK0cUiptCFUEliyQqLgeutmo8QT+myFuhOCigkd3gO/Ts/HA9efV1h3pF/80pX
hqDlXlXuHo+cqoUwCS3vdZF3BKdibV6EHy4qF/qVnECMkrspJXIVcIRc9rRy1y+MbXqEbUCxtwrJ
rm0ZY0xzh+LekunkI6e2PVdvd0g/qtccEy7f06N3TOMMZaWTSw0x9HhMloWl2ouB1S+bvFs9Yagk
Tc5aSMQNzOW5qRZ1mF48mVKRrN1rrE5D2xD5JA==

`protect key_keyowner="Xilinx", key_keyname="xilinxt_2019_02", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
U4bopG4wSqgAQnZxL2fp0S7FrDx75jbl15bXkH2mvALsB9XQUE3qdDMI92sWWRV/uzMbbqIMshjl
ZKIENZsOxjaoJ0hVcroFjOxph6nTzkmbbFkmudkJ8slcjH+xiD9RfeQFHMsXkBGLzC11PVdamyZ0
P7LdruCjryCHGCn70pBIZuh55AEoIPKbMJ9MaIkCgo37fZfwGMHUIfcvU4aDBBuf41xMf2m++S9u
RR2xaqwnsNdfcKXb+gT0yVDNqNasrMWc3PwHJvsNiY4RwM7ZSITnu8GWNRuKRlIjuYg7t9pIPzTe
eHl0DoLjHR6lVlHoVbpqWfaaUa6luuIc7u4PNQ==

`protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VELOCE-RSA", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=128)
`protect key_block
sAs2oWs8lBD4xeSCwEijiqMelKmseqrG/zdMgpoP/wZ8fFRCLUax7WNKGlE6cPnL+y3jaA/+0fhV
ndzyEbMbXXM0aG4qQzxDsJw+4KnEUAFIV17eRWZk6dOo5MnkmDxgjZixEnxP2MzFUchitx7IleaH
iKm7b7mAy39oUY8fSx4=

`protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-VERIF-SIM-RSA-2", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
eWM7fRAz99edtylcrw22vOsawXtWPeHz6UHdrRNJFlHrb+PoOiaxgGrcbYNHn9NMpDY2KUERUmu5
7u8qEumSCoU2dkcWNPpMNn9MGhIh1nzl4RJ01/o0OfiS5LtyOXkCQkzbuE2yNIPRfiygQYgD8Q+d
oGEZN/9d0Ds57Pkj3hNfGS1iNbu/7qlhcXQhcUh203/GNMxjzFCRCWCrG3EQCNAUSPsy+sebZDxg
X72jBoFo8D3NZ3K0TK/OR6j0cYLSAEvX3AUz7+0LifAWGDopG+i3152NkVbQICrPt5Wb1h01Eyfu
TVCmOrE3siGLwl6+yYH9uKwyU4tc9mQHm817lA==

`protect key_keyowner="Real Intent", key_keyname="RI-RSA-KEY-1", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
oDZ/HLJGYC65wGItiCMl8rUIIcjy2vdrgFYPPFItMXWLV/RCwZ+IAOrpA0FarBzttgv8oSNmKzjB
mNYdICjl0hImxNi9hHbN83CfIYqybRISD/cmAcL4S+aHECMc8R+FMJz0l2qphfvF8mdgxnGjc8zc
y+aB/1Db4HQH4XHiUY9nsNK7nnkaV/RdE6XIclPHqukKyLX8Tq2w/kKoBWOoWSSkG4uOC4SeEJOs
u8U6ALcCaYIStFeSuXNGAZmJ47B22XlipvApuzKJqQNsbeg5KOvWKnof/xMzPFgiqYJalJox6y/i
wpZarOwj/eINR6KiLV0yzqadWxDE9ReUY5agEg==

`protect key_keyowner="Mentor Graphics Corporation", key_keyname="MGC-PREC-RSA", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
d2OKGWr4MKn2+bdH8rjMRcY2tIrcAGNx2niWeKe6AKODPz24zXgbn3in7yNOYot337zaeCbJv9Tm
d3nNH4ZmYPX/nTjTL61y+QeHLCPyTVfsEAG6rJobX5jvzCRUrj4JRMoIjCZFIp7gZdUK9ak1wqvn
2pM6goVLkOYTeWHZl/tI11bqZpbFPKce6aVUjDSaeeX7wz9/WXCvruKCddPJE75SUWaR5VF2iqy+
gv1iOwKc98+RPVtbY7osVX42PPPA8XK31mULeLsdY5q8GmtrhQl8+yZVGIznlKfTmMKG925lyphl
tNFzK5JEz3K5l/jBmUizDkAZD4yPq5hrsMZ/6w==

`protect key_keyowner="Synplicity", key_keyname="SYNP15_1", key_method="rsa"
`protect encoding = (enctype="BASE64", line_length=76, bytes=256)
`protect key_block
v120p61vBZLwdQb2oMoK25kkQzcJBH8IPDqM3/T9MZiARhIQ46DwarIaRQyPVJBT+oGgsbjQW41W
rU711LJI5bEdzmIygWax7rROdtXhC+16YleQCqyFSO6uzKoyQg/O4th94YdJ8anGyfugF3Zvach2
FVGiETkO1lsulJI9QjpuFlSdLxiafZBaVbqbj96gRdEfL+kKYkD32KlcBNC9kWW2iLbrkbI7pt10
GQx9PvqtvB0CyA8OA/nXu0GDdDnqgP6UdLM1fyUuGMbdcRxWSQnBGkcHi18cxR5X1fxBcYA66c0G
LdtWczdSECyDCRCkMbrEaTAXaXObeiYxsIJMUQ==

`protect data_method = "AES128-CBC"
`protect encoding = (enctype = "BASE64", line_length = 76, bytes = 18768)
`protect data_block
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
MoeQFU2G4RQoWA==
`protect end_protected
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity binary_counter_c_counter_binary_v12_0_14 is
  port (
    CLK : in STD_LOGIC;
    CE : in STD_LOGIC;
    SCLR : in STD_LOGIC;
    SSET : in STD_LOGIC;
    SINIT : in STD_LOGIC;
    UP : in STD_LOGIC;
    LOAD : in STD_LOGIC;
    L : in STD_LOGIC_VECTOR ( 31 downto 0 );
    THRESH0 : out STD_LOGIC;
    Q : out STD_LOGIC_VECTOR ( 31 downto 0 )
  );
  attribute C_AINIT_VAL : string;
  attribute C_AINIT_VAL of binary_counter_c_counter_binary_v12_0_14 : entity is "0";
  attribute C_CE_OVERRIDES_SYNC : integer;
  attribute C_CE_OVERRIDES_SYNC of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_COUNT_BY : string;
  attribute C_COUNT_BY of binary_counter_c_counter_binary_v12_0_14 : entity is "1";
  attribute C_COUNT_MODE : integer;
  attribute C_COUNT_MODE of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_COUNT_TO : string;
  attribute C_COUNT_TO of binary_counter_c_counter_binary_v12_0_14 : entity is "1";
  attribute C_FB_LATENCY : integer;
  attribute C_FB_LATENCY of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_HAS_CE : integer;
  attribute C_HAS_CE of binary_counter_c_counter_binary_v12_0_14 : entity is 1;
  attribute C_HAS_LOAD : integer;
  attribute C_HAS_LOAD of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_HAS_SCLR : integer;
  attribute C_HAS_SCLR of binary_counter_c_counter_binary_v12_0_14 : entity is 1;
  attribute C_HAS_SINIT : integer;
  attribute C_HAS_SINIT of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_HAS_SSET : integer;
  attribute C_HAS_SSET of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_HAS_THRESH0 : integer;
  attribute C_HAS_THRESH0 of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_IMPLEMENTATION : integer;
  attribute C_IMPLEMENTATION of binary_counter_c_counter_binary_v12_0_14 : entity is 1;
  attribute C_LATENCY : integer;
  attribute C_LATENCY of binary_counter_c_counter_binary_v12_0_14 : entity is 1;
  attribute C_LOAD_LOW : integer;
  attribute C_LOAD_LOW of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_RESTRICT_COUNT : integer;
  attribute C_RESTRICT_COUNT of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_SCLR_OVERRIDES_SSET : integer;
  attribute C_SCLR_OVERRIDES_SSET of binary_counter_c_counter_binary_v12_0_14 : entity is 1;
  attribute C_SINIT_VAL : string;
  attribute C_SINIT_VAL of binary_counter_c_counter_binary_v12_0_14 : entity is "0";
  attribute C_THRESH0_VALUE : string;
  attribute C_THRESH0_VALUE of binary_counter_c_counter_binary_v12_0_14 : entity is "1";
  attribute C_VERBOSITY : integer;
  attribute C_VERBOSITY of binary_counter_c_counter_binary_v12_0_14 : entity is 0;
  attribute C_WIDTH : integer;
  attribute C_WIDTH of binary_counter_c_counter_binary_v12_0_14 : entity is 32;
  attribute C_XDEVICEFAMILY : string;
  attribute C_XDEVICEFAMILY of binary_counter_c_counter_binary_v12_0_14 : entity is "artix7";
  attribute downgradeipidentifiedwarnings : string;
  attribute downgradeipidentifiedwarnings of binary_counter_c_counter_binary_v12_0_14 : entity is "yes";
end binary_counter_c_counter_binary_v12_0_14;

architecture STRUCTURE of binary_counter_c_counter_binary_v12_0_14 is
  signal \<const1>\ : STD_LOGIC;
  signal NLW_i_synth_THRESH0_UNCONNECTED : STD_LOGIC;
  attribute C_AINIT_VAL of i_synth : label is "0";
  attribute C_CE_OVERRIDES_SYNC of i_synth : label is 0;
  attribute C_COUNT_BY of i_synth : label is "1";
  attribute C_COUNT_MODE of i_synth : label is 0;
  attribute C_COUNT_TO of i_synth : label is "1";
  attribute C_FB_LATENCY of i_synth : label is 0;
  attribute C_HAS_CE of i_synth : label is 1;
  attribute C_HAS_LOAD of i_synth : label is 0;
  attribute C_HAS_SCLR of i_synth : label is 1;
  attribute C_HAS_SINIT of i_synth : label is 0;
  attribute C_HAS_SSET of i_synth : label is 0;
  attribute C_HAS_THRESH0 of i_synth : label is 0;
  attribute C_IMPLEMENTATION of i_synth : label is 1;
  attribute C_LATENCY of i_synth : label is 1;
  attribute C_LOAD_LOW of i_synth : label is 0;
  attribute C_RESTRICT_COUNT of i_synth : label is 0;
  attribute C_SCLR_OVERRIDES_SSET of i_synth : label is 1;
  attribute C_SINIT_VAL of i_synth : label is "0";
  attribute C_THRESH0_VALUE of i_synth : label is "1";
  attribute C_VERBOSITY of i_synth : label is 0;
  attribute C_WIDTH of i_synth : label is 32;
  attribute C_XDEVICEFAMILY of i_synth : label is "artix7";
  attribute downgradeipidentifiedwarnings of i_synth : label is "yes";
begin
  THRESH0 <= \<const1>\;
VCC: unisim.vcomponents.VCC
     port map (
      P => \<const1>\
    );
i_synth: entity work.binary_counter_c_counter_binary_v12_0_14_viv
     port map (
      CE => CE,
      CLK => CLK,
      L(31 downto 0) => L(31 downto 0),
      LOAD => '0',
      Q(31 downto 0) => Q(31 downto 0),
      SCLR => SCLR,
      SINIT => '0',
      SSET => '0',
      THRESH0 => NLW_i_synth_THRESH0_UNCONNECTED,
      UP => '0'
    );
end STRUCTURE;
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;
entity binary_counter is
  port (
    CLK : in STD_LOGIC;
    CE : in STD_LOGIC;
    SCLR : in STD_LOGIC;
    Q : out STD_LOGIC_VECTOR ( 31 downto 0 )
  );
  attribute NotValidForBitStream : boolean;
  attribute NotValidForBitStream of binary_counter : entity is true;
  attribute CHECK_LICENSE_TYPE : string;
  attribute CHECK_LICENSE_TYPE of binary_counter : entity is "binary_counter,c_counter_binary_v12_0_14,{}";
  attribute downgradeipidentifiedwarnings : string;
  attribute downgradeipidentifiedwarnings of binary_counter : entity is "yes";
  attribute x_core_info : string;
  attribute x_core_info of binary_counter : entity is "c_counter_binary_v12_0_14,Vivado 2019.2";
end binary_counter;

architecture STRUCTURE of binary_counter is
  signal NLW_U0_THRESH0_UNCONNECTED : STD_LOGIC;
  attribute C_AINIT_VAL : string;
  attribute C_AINIT_VAL of U0 : label is "0";
  attribute C_CE_OVERRIDES_SYNC : integer;
  attribute C_CE_OVERRIDES_SYNC of U0 : label is 0;
  attribute C_COUNT_BY : string;
  attribute C_COUNT_BY of U0 : label is "1";
  attribute C_COUNT_MODE : integer;
  attribute C_COUNT_MODE of U0 : label is 0;
  attribute C_COUNT_TO : string;
  attribute C_COUNT_TO of U0 : label is "1";
  attribute C_FB_LATENCY : integer;
  attribute C_FB_LATENCY of U0 : label is 0;
  attribute C_HAS_CE : integer;
  attribute C_HAS_CE of U0 : label is 1;
  attribute C_HAS_LOAD : integer;
  attribute C_HAS_LOAD of U0 : label is 0;
  attribute C_HAS_SCLR : integer;
  attribute C_HAS_SCLR of U0 : label is 1;
  attribute C_HAS_SINIT : integer;
  attribute C_HAS_SINIT of U0 : label is 0;
  attribute C_HAS_SSET : integer;
  attribute C_HAS_SSET of U0 : label is 0;
  attribute C_HAS_THRESH0 : integer;
  attribute C_HAS_THRESH0 of U0 : label is 0;
  attribute C_IMPLEMENTATION : integer;
  attribute C_IMPLEMENTATION of U0 : label is 1;
  attribute C_LATENCY : integer;
  attribute C_LATENCY of U0 : label is 1;
  attribute C_LOAD_LOW : integer;
  attribute C_LOAD_LOW of U0 : label is 0;
  attribute C_RESTRICT_COUNT : integer;
  attribute C_RESTRICT_COUNT of U0 : label is 0;
  attribute C_SCLR_OVERRIDES_SSET : integer;
  attribute C_SCLR_OVERRIDES_SSET of U0 : label is 1;
  attribute C_SINIT_VAL : string;
  attribute C_SINIT_VAL of U0 : label is "0";
  attribute C_THRESH0_VALUE : string;
  attribute C_THRESH0_VALUE of U0 : label is "1";
  attribute C_VERBOSITY : integer;
  attribute C_VERBOSITY of U0 : label is 0;
  attribute C_WIDTH : integer;
  attribute C_WIDTH of U0 : label is 32;
  attribute C_XDEVICEFAMILY : string;
  attribute C_XDEVICEFAMILY of U0 : label is "artix7";
  attribute downgradeipidentifiedwarnings of U0 : label is "yes";
  attribute x_interface_info : string;
  attribute x_interface_info of CE : signal is "xilinx.com:signal:clockenable:1.0 ce_intf CE";
  attribute x_interface_parameter : string;
  attribute x_interface_parameter of CE : signal is "XIL_INTERFACENAME ce_intf, POLARITY ACTIVE_HIGH";
  attribute x_interface_info of CLK : signal is "xilinx.com:signal:clock:1.0 clk_intf CLK";
  attribute x_interface_parameter of CLK : signal is "XIL_INTERFACENAME clk_intf, ASSOCIATED_BUSIF q_intf:thresh0_intf:l_intf:load_intf:up_intf:sinit_intf:sset_intf, ASSOCIATED_RESET SCLR, ASSOCIATED_CLKEN CE, FREQ_HZ 10000000, PHASE 0.000, INSERT_VIP 0";
  attribute x_interface_info of SCLR : signal is "xilinx.com:signal:reset:1.0 sclr_intf RST";
  attribute x_interface_parameter of SCLR : signal is "XIL_INTERFACENAME sclr_intf, POLARITY ACTIVE_HIGH, INSERT_VIP 0";
  attribute x_interface_info of Q : signal is "xilinx.com:signal:data:1.0 q_intf DATA";
  attribute x_interface_parameter of Q : signal is "XIL_INTERFACENAME q_intf, LAYERED_METADATA undef";
begin
U0: entity work.binary_counter_c_counter_binary_v12_0_14
     port map (
      CE => CE,
      CLK => CLK,
      L(31 downto 0) => B"00000000000000000000000000000000",
      LOAD => '0',
      Q(31 downto 0) => Q(31 downto 0),
      SCLR => SCLR,
      SINIT => '0',
      SSET => '0',
      THRESH0 => NLW_U0_THRESH0_UNCONNECTED,
      UP => '1'
    );
end STRUCTURE;
