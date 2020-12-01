class Main {
    main (): Object {
        0
    };
}

class Point {
    x: Int;

    y: Int;

    init (x0: Int, y0: Int): Point {
        {
            x <- x0;
            y <- y0;
            self;
        }
    };
}