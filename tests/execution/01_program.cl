class Main inherits IO {
    number: Int <- 5;

    main () : Object {
        testing_fibonacci(number)
    };

    testing_fibonacci(n: Int) : IO {{
        out_string("Iterative Fibonacci : ");
        out_int(iterative_fibonacci(5));
        out_string("\n");

        out_string("Recursive Fibonacci : ");
        out_int(recursive_fibonacci(5));
        out_string("\n");
    }};

    recursive_fibonacci (n: AUTO_TYPE) : AUTO_TYPE {
        if n <= 2 then 1 else recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2) fi
    };

    iterative_fibonacci(n: AUTO_TYPE) : AUTO_TYPE {
        let  i: Int <- 2, n1: Int <- 1, n2: Int <- 1, temp: Int in {
            while i < n loop
                let temp: Int <- n2 in {
                    n2 <- n2 + n1;
                    n1 <- temp;
                    i <- i + 1;
                }
            pool;
            n2;
        }
    };
}