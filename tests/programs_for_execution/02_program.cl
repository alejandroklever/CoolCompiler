class Main inherits IO {
    main (): Object {
        {
            out_int((new Ackermann).ackermann(3, 2));
            out_string("\n");
        }
    };
}

class Ackermann {
    ackermann (m: Int, n: Int): Int {
        if m = 0
        then
            n + 1
        else
            if n = 0
            then
                self.ackermann(m - 1, 1)
            else
                self.ackermann(m - 1, self.ackermann(m, n - 1))
            fi
        fi
    };
}