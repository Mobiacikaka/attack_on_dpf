# Attack On DPF

## Off Line Attack

begin with file oflattack.py

### Sample

![image-20220719111529549](/home/justin/.config/Typora/typora-user-images/image-20220719111529549.png)

![Wrong Example](/home/justin/.config/Typora/typora-user-images/image-20220719111504327.png)

### Attack Reformulation

- 攻击者向量多少对攻击者能力产生影响.
- 两个攻击向量相隔越远, 它们的控制范围更大, 但控制强度更低; 也就是说两个攻击向量的控制范围和控制强度呈负相关.
  - 控制范围表示为可攻击的正常向量的数量.
  - 控制强度与可攻击的正常向量的DS的大小呈负相关. 当控制强度不够的时候, 只有DS大的正常向量才能被成功攻击.
- 攻击者获得的分配总量只和成功攻击到的向量有关, 和如何分配攻击向量的需求无关.

### How to Prune

#### ATTACKable

- 可攻击向量: 在不考虑攻击其它向量的前提下, 可以被成功单独攻击的向量.
- 不可攻击向量: 在不考虑攻击其它向量的前提下, 无论如何也无法被成功攻击的向量.

#### Collision

- 冲突有可能产生.

#### Conditioning

- 对于$DS \leq step$ 的向量, 可以果断设为不可攻击的向量.
- 对于$step < DS \leq 2 * step$ 的向量, 只有

## On Line Attack

begin with file onlattack.py
