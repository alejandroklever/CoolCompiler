class Main {
    main (): Object {
        0
    };

    f (a: Int, b: Int, c: Int, d: Int): Int {
        {
            a <- b;
            b <- c;
            c <- d;
            d <- a;
            d + 1;
            a;
        }
    };
}