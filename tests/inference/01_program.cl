class Main {
    main (): Object {
        0
    };
}

class Point {
    x: AUTO_TYPE;
    y: AUTO_TYPE;

    init(x0: Int, y0: Int): AUTO_TYPE {{
        x <- x0;
        y <- y0;
        self;
    }};
}