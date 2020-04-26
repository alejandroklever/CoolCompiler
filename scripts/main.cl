--Any characters between two dashes “--” and the next newline
--(or EOF, if there is no next newline) are treated as comments

(*(*(*
Comments may also be written by enclosing
text in (∗ . . . ∗). The latter form of comment may be nested.
Comments cannot cross file boundaries.
*)*)*)

class Main {
    main ( msg : String ) : Void {
        let a: Int <- 25, b: Int <- 15 in {
            a + +;
        }
    };
}
