class Main inherits IO {
    main (): Object {
        let id : Int,
            name : String,
            email : String in
            {
                self.out_string("Introduzca su id: ");
                id <- self.in_int();
                self.out_string("Introduzca su nombre: ");
                name <- self.in_string();
                self.out_string("Introduzca su email: ");
                email <- self.in_string();
                let user: User <- (new User).init(id, name, email) in
                    self.out_string("Created user: ".concat(user.get_name()).concat("\n"));
            }
    };
}

class User {
    id: Int;

    name: String;

    email: String;

    init (id_: Int, name_: String, email_: String): User {
        {
            id <- id_;
            name <- name_;
            email <- email_;
            self;
        }
    };

    get_name (): String {
        name
    };
}