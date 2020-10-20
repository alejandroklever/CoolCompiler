class Main {
    a: Int

    b: String

    main () : String { 
        let a: Int <- "" in 0 
    }

    function_with_errors() : Object {
        case a of
            x: Int => (new IO).out_int(x)
            y: String => (new IO).out_string(x)
        esac
    }
}