# DCPS 3.0 Document

This repository contains important information and instructions for working with the DCPS 3.0 project.

## GitHub Repositories

- DCPS 2: [https://github.com/rohithsaradhy/dcps_ddmtd_toolkit](https://github.com/rohithsaradhy/dcps_ddmtd_toolkit)
  - Clone firmware 2.4
  - Clone DCPS2

- DCPS3 Nexys Board: [https://github.com/zachariaheberle/dcps3_toolkit/tree/dcps3](https://github.com/zachariaheberle/dcps3_toolkit/tree/dcps3)

## SSH Access

To set up SSH access to the DCPS3 Nexys Board, follow these steps:

1. Run the following command: `nano ~/.ssh/config`
2. Edit the document and paste the following configuration:

```plaintext
Host nexys_ddmtd_dcps3
     	HostName nexys-radiation.local
     	User pi
     	HostKeyAlgorithms +ssh-rsa
```

## Setup Passwordless and Keygen

To set up passwordless SSH access and key generation, follow the instructions provided in this guide: [https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)

## DCPS3: Running Code

To run code on the DCPS3, follow these steps:

1. Configure the connection with the board.
2. Check if you can SSH into the Nexys board (`pi@nexys_ddmtd_dcps3`).
3. Disconnect from the SSH session.
4. Open the Jupyter Notebook.
5. Run all relevant cells necessary for data taking and plotting

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
