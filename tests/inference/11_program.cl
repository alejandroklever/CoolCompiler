class Main {
    main (): Object {
        0
    };

    f(): AUTO_TYPE {
        let x: AUTO_TYPE <- new Dog in
            case x of
                m: Mammal =>
                    case m of
                        c: Cat => create_cat();
                        d: Dog => create_dog();
                    esac;
                r: Reptile => create_reptile();
            esac
    };

    create_dog(): AUTO_TYPE {
        new Dog
    };

    create_cat(): AUTO_TYPE {
        new Cat
    };

    create_reptile(): AUTO_TYPE {
        new Reptile
    };
}

class Animal {}
class Mammal inherits Animal {}
class Reptile inherits Animal {}
class Dog inherits Mammal {}
class Cat inherits Mammal {}