class Main inherits IO {
    main (): IO {
        let vector: Vector2 <- (new Vector2).init(0, 0) in
            vector.print_vector()
    };
}

class Vector2 {
    x: Int;

    y: Int;

    init (x_: Int, y_: Int): Vector2 {
        {
            x <- x_;
            y <- y_;
            self;
        }
    };

    get_x (): Int {
        x
    };

    get_y (): Int {
        y
    };

    add (v: Vector2): Vector2 {
        (new Vector2).init(x + v.get_x(), y + v.get_y())
    };

    print_vector (): IO {
        let io: IO <- (new IO) in
            {
                io.out_string("(");
                io.out_int(self.get_x());
                io.out_string("; ");
                io.out_int(self.get_y());
                io.out_string(")\n");
            }
    };

    clone_vector (): Vector2 {
        (new Vector2).init(x, y)
    };
}