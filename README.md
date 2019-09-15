# Ardupy_Code_Generator
Generate common-hal and binding level code for Ardupy.

### Generate
```bash
python gen.py info.json
```

### Uages
#### Example 1
```json
{
    "some_module" : {
        "void some_function(int a b, pin scl dat)": {
            "chk" : {
                "a"   : "1"      //'a' needs to be equal to 1 
                "b"   : "-1,1,2" //'b' should be among -1,1,2
                "scl" : "SCL"    //'scl' needs match the 'SCL' pin
                "dat" : "D0,D1"  //'scl' needs match the 'D0' or 'D1' pin
            }
        }
    }
}
```

#### Example 2
```json
{
    "some_module" : {
        "void some_function(int a b c d e f g h i j)": {
            "chk" : {
                "a" : "[0,]"     //'a' needs to be large equal than 0 and less equal than max int
                "b" : "[,0]"     //'b' needs to be large equal than min int and less equal than 0 
                "c" : "(0,]"     //'c' needs to be large than 0 and less equal than max int
                "d" : "[,0)"     //'d' needs to be large equal than min int and less than 0 
                "e" : "[1,8]"    //'e' needs to be large equal than 1 and less equal than 8
                "f" : "[9,100)"  //'f' needs to be large equal than 9 and less than 100
                "g" : "(16,30]"  //'g' needs to be large than 16 and less equal than 30
                "h" : "(-10,0)"  //'h' needs to be large than -10 and less than 0
                "i" : "[,4],[9,]"//'i' needs to be large equal than 9 or less equal than 4
                "j" : "[,1),(7,]"//'i' needs to be large than 7 or less than 1
            }
        }
    }
}
```

#### Example 3
```json
{
    "i2c" : { //1st module
        "void i2c(pin scl sda, int frequency=400000 timeout=255)": { //a parameter can with default value
            "chk" : {
                "scl" : "SCL",
                "sda" : "SDA",
                "frequency" : "[400000,]",
                "timout" : "255,127,63"
            }
        },
        "int get_int()" : {}
        "str get_str()" : {}
        "obj get_obj()" : {}
        "bool get_bool()" : {}
        "float get_float()" : {}
        "void say_hello()" : {}
        "void set_int(int value)" : {}
        "void get_str(str value)" : {}
        "void set_obj(obj value)" : {}
        "void set_pin(pin value)" : {}
        "void get_bool(bool value)" : {}
        "void set_float(float value)" : {}
    },
    "spi" : { //2nd module
        ...
    },
    "uart" : { //3rd module
        ...
    }
}
```