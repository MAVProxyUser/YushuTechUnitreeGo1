All the magic can be found here:
https://github.com/unitreerobotics/unitree_legged_sdk/issues/24

Thanks to Devemin:
https://qiita.com/devemin/items/1708176248a1928f3b88

Requirements:
Do not use one of these versions of the SDK, because they do NOT support go1:
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.2
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.3
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.3.1
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.3.2
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/3.3.3
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/3.3.4
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.8.1
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.8.2
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.8.3
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.8.4

Support for go1 is only found in these versions:
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/3.4.2 
```
- Legged_sport >= v1.32
```
https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.5.0
```
- Legged_sport    >= v1.36.0
- firmware H0.1.7 >= v0.1.35
           H0.1.9 >= v0.1.35
```

https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.5.1
```
- Legged_sport    >= v1.36.0
- firmware H0.1.7 >= v0.1.35
           H0.1.9 >= v0.1.35
```

https://github.com/unitreerobotics/unitree_legged_sdk/releases/tag/v3.8.0
```
- Legged_sport    >= v1.36.0
- firmware H0.1.7 >= v0.1.35
           H0.1.9 >= v0.1.35
  g++             >= v8.3.0
  python             3.7.x
                     3.8.x
```

Alternative typo patched fork for go1 v3.5.1:
https://github.com/JonasFovea/unitree_legged_sdk/tree/fix

You MUST patch the example_walk.cpp to work with High Level if you have an (Air?) Pro, or MAX (non EDU version)

You need to use: 
```
safe(LeggedType::Go1)
```
and 
```
192.168.123.161
```
Make sure it is not set to 
```
safe(LeggedType::A1)``` 
or 
```
192.168.123.11
```

