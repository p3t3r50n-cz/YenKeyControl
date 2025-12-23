# Yenkee YKB3700 Rogue Keyboard Protocol Documentation and Command-line Utilities

![Yenkee YKB3700 Rogue Keyboard](./images/YKB3700.png)

## Reverse Engineering Project

This comprehensive documentation and command-line utilites are the result of meticulous reverse engineering of the Yenkee YKB3700 Rogue (and probably others based on a similar ROYUAN chipset) keyboard protocol. Unlike many manufacturers who provide open APIs or cross-platform support, the vendor only offers proprietary Windows software, effectively locking out Linux, macOS, and other operating system users from customizing their RGB lighting experience.

**Our mission:** To liberate this excellent mechanical keyboard from its Windows-only shackles and empower the open-source community with complete control over its RGB lighting capabilities.

## Repository structure

### Documentation
- **[Communication Protocol](/docs/communication-protocol.md)**  
  Complete protocol documentation with uncovered commands, capabilities, and packet structures.

### Source Code
- **[YenKey Proto](/src/yenkey-proto.py)**  
  Simple prototyping script for functionality verification and packet debugging.  
  *Documentation: [yenkey-proto](/docs/yenkey-proto.md)*

- **[YenKey CLI](/src/yenkey-cli.py)**  
  Complete command-line utility for backlight effects, key colors, and key remapping.  
  *Documentation: [yenkey-cli](/docs/yenkey-cli.md)*

### Communication Protocol Documentation Structure

This documentation is divided into main sections:

1. [**Backlight Effects Protocol**](/docs/communication-protocol.md#backlight-effects-protocol) - Control global effects, colors, brightness, and animation speeds
2. [**Per-Key RGB Control**](/docs/communication-protocol.md#key-color-protocol) - Individual key color programming (see separate documentation)
3. [**Per-Key remapping**](/docs/communication-protocol.md#key-remapping-protocol) - Describes the options for reassigning individual keys to different functions (e.g., sending different scancodes)
4. [**Read Configuration from keyboard**](/docs/communication-protocol.md#read-configuration-protocol) - Describes the options for reassigning individual keys to different functions (e.g., sending different scancodes)
5. [**Audio Reaction**](/docs/communication-protocol.md#audio-reaction-protocol) - Describes the options for audio reaction

### What We've Uncovered

Through careful analysis, we've successfully decoded:
- Complete packet structure for all lighting effects
- 25 different lighting modes with submode variations
- Custom RGB color implementation for individual keys
- Key remapping implementation
- Speed and brightness control parameters
- Checksum calculation algorithm
- Proper packet sequencing and timing

### Why This Matters

This project enables:
- **Cross-platform support** - Linux, macOS, BSD, etc.
- **Custom software** - Create your own lighting controllers
- **Scripting integration** - Programmatic control for workflows
- **Open source projects** - Community-driven improvements
- **Long-term compatibility** - No reliance on vendor software updates

### Device informations

 - **USB VID:** 3151
 - **USB PID:** 4002

**Output from `lsusb`**
```
lsusb -v -d 3151:4002

Bus 002 Device 115: ID 3151:4002  FK2102T-C
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               2.00
  bDeviceClass            0
  bDeviceSubClass         0
  bDeviceProtocol         0
  bMaxPacketSize0        64
  idVendor           0x3151
  idProduct          0x4002
  bcdDevice            2.01
  iManufacturer           0
  iProduct                2 FK2102T-C
  iSerial                 0
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x003b
    bNumInterfaces          2
    bConfigurationValue     1
    iConfiguration          0
    bmAttributes         0xa0
      (Bus Powered)
      Remote Wakeup
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      1 Boot Interface Subclass
      bInterfaceProtocol      1 Keyboard
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      89
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0008  1x 8 bytes
        bInterval               1
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        1
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0
      bInterfaceProtocol      0
      iInterface              0
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength     158
         Report Descriptors:
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x82  EP 2 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0010  1x 16 bytes
        bInterval               1
Device Status:     0x0000
  (Bus Powered)
```

## Other Devices Probably Supported

List of other keyboards that may be compatible with this communication protocol and CLI utility:

Device ID | Device Name | Tested
----------|-------------|--------
**yc200_fk2102** | **FK2102T-C** | tested (Yenkee YKB3700 Rogue)
bk100_3087rf_24_2m | 3087rf
bk100_3108s | 3108rf
dk2017 | dk2017
helpBK | help
help | help
helpYZW | help
k68_elite | Elite
k68_elite_pro | Elite Pro
k68_g68 | G68
k68_hf68 | HF68
k68_hyekyu | HYEKYU
k68_kb61 | 跬步61
k68_kg008 | EK387W
k68_kl68_dm | VX6
k68_kl | 狂麟68
k68_k217 | CMK87
k68_k219 | FL680
k68_k220 | FL980CPM
k68_k223 | FL1080
k68_k237 | FL980V2
k68_k669 | FL870
k68_k84_dm | EK384
k68_k84_2m | 狂麟0824
k68_k84 | 狂麟0824
k68_lp87 | LP87
k68_magnet | MAGNET
k68_mhx | DAGK 6064
k68_mk1 | SK1
k68_m61_2m | Hot-swap
k68_pro | 雷神KC3068
k68_sk1 | SK1
k68_tk568 | TK568
k68_vl96 | 狂麟VL96
k68_voyager68 | VOYAGER68
k68_x90_3m | X90三模
k68 | 雷神KC3068
ry108 | ROYUAN108
yc200_acr_pro_68 | ACR Pro68
yc200_acr_pro_75 | ACR Pro75
yc200_ac067 | AC067
yc200_bk980 | K7 PRO
yc200_b67 | B67
yc200common | yc_common
yc200_dk2912 | F33 三模键盘
yc200_dk2922 | F87 歼星舰
yc200_domikey | DMK81
yc200_feker_ik75 | IK75 WAP
yc200_fk5011gb | MF34
yc200_f081 | FANCY81
yc200_hf67 | HF67 AP
yc200_hf67 | HF67 WAP
yc200_k220 | 220 WAP
yc200_k224 | CMK98
yc200_k232 | Q75
yc200_k401t | R68
yc200_k411t | K411t
yc200_k61 | GemRise K61
yc200_k87 | GemRise K87
yc200_k87 | k87
yc200_k980 | K980
yc200_lk67 | LK67 AP
yc200_lk67 | LK67 WAP
yc200_lp84 | lp84 AP
yc200_lp84 | lp84 WAP
yc200_l10 | L10 RGB
yc200_l8 | L8 RGB
yc200_l9 | L9 RGB
yc200_mk108l_uk | MK108L
yc200_mk11 | 5075B Plus
yc200_mk15 | DAGK 6068
yc200_nj68 | NJ68 AP
yc200_nj68 | NJ68 WAP
yc200_nj80 | nj80 AP
yc200_nj80 | nj80 WAP
yc200_pc75b | PC75B Plus
yc200_sg8821_24_2m_single | 机械战警104
yc200_sg8835_bt_2m | AK40S
yc200_sg8836_single_3m | AK35iPro
yc200_sg8843 | K515T
yc200_sg8845_24_single_2m | DKW150
yc200_sg8857_24_single_2m | SKW131
yc200_sk63 | SK63
yc200_sk66 | SK66
yc200_sk72 | KT75
yc200_vn66 | VN66 wap
yc200_3084b | 3084B
yc200_5108 | 5108 AP
yc200_5108 | 5108 WAP
yc300_abko_ar75 | ABKO AR75
yc300_acr_pro68_s_dm | ACR Pro68
yc300_acr_pro75s_dm | ACR Pro75
yc300_acr68pile | Acr68 Pile
yc300_ac067_dm | AC067
yc300_ak816 | AK816
yc300_alice_dm | ACR Alice+
yc300_alice_s_dm | Alice
yc300_ck75 | CK75
yc300_ck98 | CK98
yc300_c84 | C84
yc300_dk730 | Y5
yc300_dk731 | Y3
yc300_dk732 | Y2
yc300_dk733 | dk733
yc300_dk738 | dk738
yc300_dukharo_vn80 | VN80 WAP
yc300_dukharo_vn80 |  WAP
yc300_dz61 | DZ61
yc300_d84 | D84
yc300_ec66 | Eclipse66 wap
yc300_ek3000_2m_bt | EK3000
yc300_ep21_dm | EP-21
yc300_fek75s | FEK75S
yc300_f108 | F108
yc300_gi80 | GI80
yc300_gm081 | GM081
yc300_gm807 | K870T Pro
yc300_gm885_dm | GM884
yc300_gm885 | KB1916
yc300_g691_krux_dm | MECA 6X PLUS
yc300_g691_krux | MECA 6X PLUS
yc300_hs_g20 | G20RGB
yc300_hs_k61 | K61 PRO
yc300_ik98 | IK98
yc300_kb751 | NK751
yc300_kc108 | KC108
yc300_kc21_dm | KC21
yc300_kf100 | KF100
yc300_kf1800 | KF1800
yc300_kg006_single | MC KB108
yc300_kg039 | CK600
yc300_kg043 | KR-081
yc300_kg045 | CR-960
yc300_kiiboom81 | KiiBoom81
yc300_kt002b_bt_2m | GK301
yc300_k219 | FL680WAP
yc300_k224b | CMK98PRO
yc300_k235 | FL750
yc300_k237 | FL980V2
yc300_k239 | Q75-knob
yc300_k401t | K401T
yc300_k402t | R100
yc300_k402t_single | K402t
yc300_k403t | R108
yc300_k403t_single | K403t
yc300_k64_single | K64
yc300_k9Pro | K9 PRO
yc300_k980 | K980
yc300_k980_oled | K980
yc300_maxfit108_dm | Maxfit108
yc300_maxfit87_dm | Maxfit87
yc300_mek26_75_dm | Noir Z2
yc300_mek27_65_dm | Noir Z1
yc300_mg108_dm | MG108
yc300_mkga75_jp_24_2m | UP-MKGA75-J
yc300_mkga75_24_2m | UP-MKGA75-A
yc300_mk15_dm | RX-D68
yc300_mk15_uk | MK68
yc300_mk857_dm | MAXFIT 61
yc300_mk857 | MAXFIT 61
yc300_mmd_k87pro | K87Pro
yc300_m84x | DAXA M84X
yc300_nk100 | Nk100 WAP
yc300_pc75s_dm | PC75S
yc300_pc75_s_mac_white_plus | PC75B Plus
yc300_pc75_s_plus | PC75B Plus
yc300_pc75s_s_dm | PC75S
yc300_pc75_s_white_plus | PC75B Plus
yc300_pc98bplus_mac_s | PC98B Plus
yc300_pc98bplus_s | PC98B Plus
yc300_rs6 | RS6
yc300_rx980 | RX980
yc300_r87 | ROYALAXE R87
yc300_sg8821_24_2m_single | 机械战警104
yc300_sg8835_single | AK40Pro
yc300_sg8835_2m_24_single | AK40S 2.4G
yc300_sg8857_single_3m | SKW131
yc300_sg8886 | K33T
yc300_sg8886_single | K33T
yc300_sg8922 | K081T
yc300_sg8925 | AK692
yc300_sg8925_single | AK692
yc300_skyline87 | Skyline 87
yc300_sk5_dm | SK5 wired
yc300_sk5 | SK5
yc300_sk6_dm | SK6 wired
yc300_sk6 | SK6
yc300_sk81 | SK81
yc300_s3087 | S3087
yc300_s68 | S68 WAP
yc300_th96 | th96 WAP
yc300_tk63pro | TK-63 Pro
yc300_t98_dm | T98
yc300_t98 | T98
yc300_vn96 | VN96 WAP
yc300_w_87 | W-87 WAP
yc300_yc75 | YC75
yc300_yk630us_a | K63套件
yc300_yk700_bt_2m | YK700 BT
yc300_yk700_24_2m | YK700 24
yc300_yz21_dm | YZ-21
yc300_y68 | ROYALAXE Y68
yc300_zsx61 | Maxfit61 Pro
yc300_3068beu_plus_uk | 3068BEU Plus
yc300_3068b_plus | 3068B Plus
yc300_3068s_dm | 3068S
yc300_3084s_dm | 3084S
yc300_5075b_plus_s | 5075B Plus
yc300_5075s_dm | 5075S
yc300_5075s_s_dm | 5075S
yc300_5087beu_plus_uk | 5087BEU Plus
yc300_5087b_plus | 5087B Plus
yc300_5087s_dm | 5087S
yc300_5087seu_dm | 5087SEU
yc300_5108b_plus_uk | 5108BEU Plus
yc300_5108s_dm | 5108S
yc300_5108s_white_dm | 5108S
yc300_5108_white | 5108S
yc300_61k_dm | XS61K
yc300_75v5 | 75V5
yc300_940v5 | 940V5
yc400_a84 | A84
yc400_dk67_langao3 | DK67Pro
yc400_nj68 | nj68 AP
yc400_nj68 | nj68 WAP
yc400_y87 | Y87
yc400_y98 | Y98
yc500_dk730 | Y5
yc500_dk731 | Y3
yc500_dk732 | Y2
yc500_f081 | FANCY81
yc500_hf67 | HF67 AP
yc500_hf67 | HF67 WAP
yc500_hs_k61 | K61 PRO
yc500_k202s | K202S
yc500_k980_oled | K980
yc500_nj80 | nj80SOC
yc500_nj80 | nj80SOC WAP
yc500_nj80 | YC500
yc500_nj80 | YC500 WAP
yc500_pc75b | PC75B Plus
yc500_rx980 | RX980
yc500_vn66 | VN66 wap
yc500_y98 | Y98
yc500_zsx68 | MAXFIT67
yc500_3068beu_plus_uk | 3068BEU Plus
yc500_3068_plus | 3068B Plus
yzw_ak67_dm | MOD005
yzw_ak75_dm | MOD007
yzw_ak980_dm | MOD003/004
yzw_an63_dm | RTK63P
yzw_baota98 | ML-980
yzw_bk980 | K7 PRO
yzw_boyi_68 | Hot-swap
yzw_ck61 | CK61
yzw_ck68 | CK68
yzw_ck87 | CK87
yzw_cl87 | C87
yzw_cl87_2m | yzw_cl87_2m
YZWCommon | ROYUAN108
YZWCommon | YZW3151
yzw_cy_th66 | TH66
yzw_cy_th68 | TH68
yzw_cy_th80 | TH80
yzw_cy_th98 | TH98
yzw_dk67 | DK67
yzw_dk67_g691 | MECA 6 PLUS
yzw_dk67_g691_2m_bt | GKB610R BT
yzw_dk67_k700x_dm | Niceboy
yzw_dk670_bt_2m | GKB610R BT
yzw_dk710b | BOX 710
yzw_dk870 | CK88BT
yzw_dy_k68 | CK181 PRO
yzw_eclair75 | Eclair 75
yzw_ec66 | EC66
yzw_ek384wv2_noled | EK384W v2
yzw_elite | Elite
yzw_elite | Elite Pro
yzw_ep68_dm | EP68
yzw_ep68 | EP68BL
yzw_ep84_dm | EP84
yzw_ep84 | EP84
yzw_feker_ik75 | IK75
yzw_fk2102_c_bt_2m | FK2102_C_BT
yzw_fk2102 | FK2102T-C
yzw_fk2102 | MK108L
yzw_fk2102t_uk | FK2102T-UK
yzw_gamakay | TK68
yzw_gemrise_k64 | GemRise K64
yzw_gemrise_k68 | GemRise K68
yzw_gike_s87 | GIKE S87
yzw_gm308 | GM308
yzw_gm308_uk | GM308 UK
yzw_gm807_dm | ABM307
yzw_gm884 | OLV75
yzw_gm898_bt_2m | RAVANA
yzw_gm898 | RAVANA
yzw_gt6 | GT-6
yzw_gt8 | GT-8
yzw_gzk61 | TK-61Pro
yzw_gzk61_2m_bt | GZK61
yzw_gz84 | GZ84
yzw_gz87 | GZ-87
yzw_hf67_dm | HF67
yzw_hf67_uk_dm | HF67K
yzw_hf68 | HF68
yzw_ik75 | 75V3
yzw_kb910_g682_noled | EK396W v2
yzw_kb910_x38 | Hatsiu
yzw_kc68_dm | KC68
yzw_kc68 | Gz-68
yzw_kc84_dm | KC84
yzw_kc84 | KC-84
yzw_kn67 | KN67
yzw_kono68 | Kono 68
yzw_kono96 | Kono 96
yzw_kr081 | Qeeke Kr081
yzw_k081t_dm | AC081
yzw_k100 | K100Max
yzw_k178 | K178-104K
yzw_k181_61k_dm | K181-61K
yzw_k181_61 | K181-61
yzw_k210 | MK870
yzw_k219 | FL680
yzw_k220 | FL980CPM
yzw_k229 | CMK68
yzw_k231 | CMK61
yzw_k411t | K411t
yzw_k65_2m | Teclado KAI
yzw_k66 | K66
yzw_k67_g691_krux_dm | Krux Atax65%
yzw_k67_g691_krux_2m_bt | Krux Atax65% Wireless
yzw_k68_dm | 汉武帝68V2
yzw_k68_2m_bt | K68-BT
yzw_k68 | 雷神KC3068
yzw_k690t | K690T
yzw_k80 | K80
yzw_k84_dm | yzw_k84_dm
yzw_k84 | yzw_k84
yzw_k84_2m | yzw_k84_2m
yzw_k87_dm | K87
yzw_k98_dm | K98
yzw_k98 | Tom980-CP
yzw_k980 | yzw_k980
yzw_k980 | 圣火令98
yzw_lk67 | LK67
yzw_lp104_dm | MK8 104
yzw_lp84 | G08RGB
yzw_lp84_norgb | yzw_lp84_norgb
yzw_lp87_dm | MK8 87
yzw_lp98_dm | MK980
yzw_MilerGM898 | GM898
yzw_mk1064 | DAGK 6064V2
yzw_mk1064_dm | DAXA M64
yzw_mk3108 | MK3108
yzw_mk61max | MK61Max
yzw_mk68max | MK68Max
yzw_mk680_lite | MK680 LITE
yzw_mk680 | MK680
yzw_mk840 | MK840
yzw_mk970_dm | MK980 PRO
yzw_mk970 | MK980 PRO
yzw_mod006_dm | MOD006
yzw_mod007s_dm | MOD007S
yzw_mod008_dm | MOD008
yzw_my_rtk61b_2m_bt | RTK61B
yzw_my_rtk68bp_2m_bt | RTK68BP
yzw_m68 | M68
yzw_nj68 | NJ68
yzw_nj80 | NJ80
yzw_nk100 | K87Pro
yzw_nk100 | Nk100
yzw_nk100 | NK100
yzw_nk750al_dm | 圣火令75
yzw_qk700_2m_bt | QK700
yzw_ravanaPro | RAVANA PRO
yzw_rogue | ROGUE
yzw_rs1 | RS1
yzw_rx980_dm | RX980
yzw_rx980 | RX980
yzw_sadeskunai | SADES KUNAI
yzw_sk1 | SK1
yzw_sk3 | SK3
yzw_sk98 | yzw_sk98
yzw_s68_dm | GK S68
yzw_s68 | GK S68
yzw_tk63 | TK-63
yzw_ty61_2m | RTK61BP
yzw_ty63_2m | RTK63B
yzw_veil80 | Veil80
yzw_vl68 | yzw_vl68
yzw_vl96 | yzw_vl96
yzw_vn66 | VN66
yzw_vn80 | VN80
yzw_woaommd75 | MMD75
yzw_w_87 | W-87
yzw_yk600 | YK600
yzw_yzi68 | YZI
yzw_yzi84 | YZI84
yzw_yz68_dm | YZ68
yzw_yz84_dm | YZ84
yzw_zen67 | ZEN67
yzw_zsx68 | MAXFIT67
yzw_3068 | Akko 3068B
yzw_3084 | 3084B
yzw_3098 | Akko 3098B
yzw_5087 | akko_5087
yzw_5108 | Akko 5108B
yzw_61m | APOLLO61 V2
yzw_61m_dm | Virgo RGB
yzw_881_dm_uk | TE-BKL001
yzw_940v3 | 940v3
yzw_955 | S.T.R.I.K.E. 8

### ⚠️ Legal Notice

This project was created through clean-room reverse engineering for interoperability purposes. All trademarks remain property of their respective owners. This project aims to enhance user experience, not circumvent legitimate copyright protections.

*Join us in celebrating the spirit of open hardware and software freedom! **Feel free to modify or fork** :-)*
