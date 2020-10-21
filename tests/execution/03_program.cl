class A { }

class B inherits A { }

class C inherits A { }

class Main inherits IO {
    main () : Object {
        testing_case()
    };

    testing_case() : IO {
        let a: A <- new C in
            case a of
                x: B => out_string("Is type B.\n");
                x: C => out_string("Is type C.\n");
            esac
    };
}