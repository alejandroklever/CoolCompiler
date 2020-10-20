(* Testing IO *)
class Main inherits IO {

    main(): Object {
        let id: AUTO_TYPE, name: AUTO_TYPE, email: AUTO_TYPE in {
            out_string("Introduzca su id: ");
            id <- self.in_int();
            out_string("Introduzca su nombre: ");
            name <- self.in_string();
            out_string("Introduzca su email: ");
            email <- self.in_string();
            let user: AUTO_TYPE <- (new User).init(id, name, email) in
                out_string("Created user: ".concat(user.get_name()).concat("\n"));
        }
    };
}

class User {
    id: AUTO_TYPE;
    name: AUTO_TYPE;
    email: AUTO_TYPE;

    init(id_: AUTO_TYPE, name_: AUTO_TYPE, email_: AUTO_TYPE): AUTO_TYPE {{
        id <- id_;
        name <- name_;
        email <- email_;
        self;
    }};

    get_name(): AUTO_TYPE {
        name
    };
}