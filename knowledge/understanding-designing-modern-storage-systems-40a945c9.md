# Lecture General Structure

| Lecture Name | Slide’s URL | Lecture’s URL |
|---|---|---|
| Basics of NAND Flash-Based SSDs |  | [Fall 2026](https://www.youtube.com/watch?v=g3wAlENrsj0&list=PLcQYzfBAwuFs&index=2)  [Spring 2026](https://www.youtube.com/watch?v=GhfMpT5ep3A&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=2) |
| Introduction to MQSim |  | [Fall 2026](https://www.youtube.com/watch?v=CA7Mb99qkCU&list=PLcQYzfBAwuFs&index=3)  [Spring 2026](https://www.youtube.com/watch?v=9YZGHl6yxBc&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=3) |
| Processing Inside NAND Flash Memory |  | [Fall 2026](https://www.youtube.com/watch?v=7SJUBQbYbRM&list=PLcQYzfBAwuFs&index=4)  [Spring 2026 Lecture I](https://www.youtube.com/watch?v=Oi6ZTViWaNA&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=4)  [Spring 2026 Lecture II](https://www.youtube.com/watch?v=Oi6ZTViWaNA&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=4) |
| Cutting-Edge Research in Flash Memory |  | [Fall 2026](https://www.youtube.com/watch?v=k--kw0ExHzU&list=PLcQYzfBAwuFs&index=5) |
| SSD Performance and Advanced Flash Commands |  | [Spring 2026](https://www.youtube.com/watch?v=Oi6ZTViWaNA&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=4) |
| Address Translation and Garbage Collection |  | [Spring 2026](https://www.youtube.com/watch?v=Oi6ZTViWaNA&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=4) |
| Flash Memory & Solid-State Drives |  | [Spring 2026](https://www.youtube.com/watch?v=Oi6ZTViWaNA&list=PL5Q2soXY2Zi9OtbGJyUVHp1Gp3c_0Dymh&index=4) |

# Modern SSD Architecture

A Modern SSD is a complicated system that consists of multiple cores, HW controllers, DRAM, and NAND flash memory packages.

![](knowledge/assets/40a945c9dc438081bd25f9a85a724f16/01.png)

![](knowledge/assets/40a945c9dc438081bd25f9a85a724f16/02.png)

## Why So Complicated?

To provide backward compatibility with traditional HDDs;

- Smaller sectors than file-system blocks: 512 Bytes vs 4 KiB
- Support overwrites

While hiding unique characteristics of NAND flash memory;

- Large operation units: Read/Write granularity (4 - 16 KiB)
- Erase-before-write property: A page needs to be first erased before programming
- Asymmetry in operation units: Erase granularity - block (hunderts or thousands of pages)
  - In place update (overwrite) is very inefficient for NAND flash memory → Out-of-Place Write & Garbage Collection
- Limited endurance: A flash cell cannot reliably store data after experiencing a certain number of program and erase (P/E) cycles
  - SLC (Single-Level Cell): > 100K P/E cycles
  - MLC (Multi-Level Cell): ~ 10K P/E cycles
  - TLC (Triple-Level Cell): < 3K P/E cycles
  - QLC (Quad-Level Cell): < 1K P/E cycles

  Requires proper lifetime management techniques (wear-levelling)

- Various error sources
- Asymmetry in operation latencies

## Flash Translation Layer - FTL

Sophisticated SSD firmware

![](knowledge/assets/40a945c9dc438081bd25f9a85a724f16/03.png)

## SSD Optmization

Requires comprehensive understanding of

- Microarchitecture of underlying NAND flash chips (HW)
- Various internal management tasks (HW and SW)
- OS & Workload characteristics (SW)

Optimization at one level may affect and/or be affected by the efficiency of designs at other levels.
