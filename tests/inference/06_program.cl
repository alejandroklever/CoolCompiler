class Main inherits IO {
    main(): IO {
        let vector: AUTO_TYPE <- (new Vector2).init(0, 0) in
            vector.print_vector()
    };
}

class Vector2 {
    x: AUTO_TYPE;
    y: AUTO_TYPE;

    init(x_: AUTO_TYPE, y_: AUTO_TYPE): AUTO_TYPE {{
        x <- x_;
        y <- y_;
        self;
    }};


    get_x(): AUTO_TYPE {
        x
    };

    get_y(): AUTO_TYPE {
        y
    };

    add(v: Vector2): AUTO_TYPE {
        (new Vector2).init(x + v.get_x(), y + v.get_y())
    };

    print_vector(): AUTO_TYPE {
        let io: IO <- new IO in {
            io.out_string("(");
            io.out_int(get_x());
            io.out_string("; ");
            io.out_int(get_y());
            io.out_string(")\n");
        }
    };

    clone_vector(): AUTO_TYPE {
        (new Vector2).init(x, y)
    };
}