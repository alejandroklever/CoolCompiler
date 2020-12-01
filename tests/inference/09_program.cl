class Main {
    main (): Object {
        0
    };
}

class Point {
    x: Int;
    y: Int;

    init(x0: AUTO_TYPE, y0: AUTO_TYPE): AUTO_TYPE {{
        x <- x0;
        y <- y0;
        self;
    }};
}