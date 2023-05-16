# DCPS 3.0 Document

This repository contains important information and instructions for working with the DCPS 3.0 project.

## GitHub Repositories

- DCPS 2: [https://github.com/rohithsaradhy/dcps_ddmtd_toolkit](https://github.com/rohithsaradhy/dcps_ddmtd_toolkit)
  - Clone firmware 2.4
  - Clone DCPS2

- DCPS3 Nexys Board: [https://github.com/akshaynaik16/dcps3_toolkit/tree/dcps3](https://github.com/akshaynaik16/dcps3_toolkit/tree/dcps3)

## SSH Access

To set up SSH access to the DCPS3 Nexys Board, follow these steps:

1. Run the following command: `sudo vim ~/.ssh/config`
2. Edit the document and paste the following configuration:

```plaintext
Host board2_trenz
        Hostname 192.168.29.11
        User root
        ProxyCommand ssh -W %h:%p board2_pi

Host board1_pi
        Hostname 192.168.29.13
        User pi
        #ProxyCommand ssh -W %h:%p lab

Host board1_trenz
        Hostname 192.168.29.12
        User root
        #ProxyCommand ssh -W %h:%p board1_pi

Host board3_pi
        Hostname 192.168.29.14
        User pi
        #ProxyCommand ssh -W %h:%p lab

Host board3_trenz
        Hostname 192.168.29.15
        User root
        #ProxyCommand ssh -W %h:%p board3_pi

Host nexys_ddmtd_dcps3
     	HostName 192.168.29.16
     	User pi
     	HostKeyAlgorithms +ssh-rsa
     	#ProxyCommand ssh -W %h:%p lab
```

## Setup Passwordless and Keygen

To set up passwordless SSH access and key generation, follow the instructions provided in this guide: [https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)

## DCPS3: Running Code

To run code on the DCPS3, follow these steps:

1. Configure the connection with the board.
2. Check if you can SSH into the Nexys board (`pi@nexys_ddmtd_dcps3`).
3. Disconnect from the SSH session.
4. Open the Jupyter Notebook.
5. Run all cells within the PLL config section.
6. Run the relevant cells in the Data Acquisition section.
7. Run the Test DCPS code.

## DCPS3: Setting Values

For the DCPS3, use the following value ranges:

- Coarse Cells: 0 - 31 (8 ps intervals)
- Fine Cells: 0 - 66 (~0.25 ps intervals)
- Channels: 2 or 3
- Tuning Bits: 2 or 3 [stage4 and stage 5]
  - 2 underestimates
  - 3 overestimates

Order of data call:

```plaintext
{fine_control}
{coarse_control}
{stage4_tune}
{stage5_tune}
{channel}
{server}
```

Order of operations:

1. Get Data (make sure to change the run name, add a date if desired).
2. Process Data (Ensure run names are consistent).
3. Plot data using the `plotDCPS` Jupyter Notebook.

## Plots Showing Different Configurations

This section includes plots demonstrating different configurations of the DCPS 3.0 project.

## DCPS 3.0 Tests

This section outlines the tests conducted for DCPS 3.0:

- Signal Integrity: Measured with a spectral analyzer using Yaya Touze's machinery.
  - Measure the signal's spectrum along with the harmonics using Fourier transform.
  - Identify and analyze other harmonics (5 - 6 Hz away).
  - Analyze signal degradation.
- Thermal Stability Tests: Temperature tests using the thermal chamber to analyze the impact on the mezzanine board.
  - Frequency stability of delays.
  - Supply with fixed 160 MHz clock.
  - Test at 320 Hz, 80 Hz, and 40 Hz frequencies.
  - Observe changes at higher frequencies.
