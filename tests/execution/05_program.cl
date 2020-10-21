class Main {
    main (): Object {
        let total: Int <- 10,
            i: Int <- 1,
            io: IO <- (new IO) in
            while i <= total loop
                 {
                    io.out_int(self.fibonacci(i));
                    io.out_string("\n");
                    i <- i + 1;
                }
            pool
    };

    fibonacci (n: Int): Int {
        if n <= 2
        then
            1
        else
            self.fibonacci(n - 1) + self.fibonacci(n - 2)
        fi
    };
}