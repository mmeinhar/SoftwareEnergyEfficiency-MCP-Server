/*
Snippets of energy inefficient Java code to test the Software Energy Efficiency MCP Server.
*/
public class Examples1 {
    static String string1; // static is inefficient. Avoid if possible
    static String string2 = "test"; // static is inefficient. Avoid if possible

    long private example1_1() {
        Long a = 4; // wrapper-class objects are less energy efficient than primitive
        int t_operator = (a > b) ? a : b; // ternary operator is less energy efficient than using if-then-else
        Vector<Integer> vector = new Vector<>(); // CopyOnWriteArrayList consumes less energy than Vector for traversal operations.

        for (long j = 1; j < iter; j++) {
            for (long k = 1; k < i ter; k++) {
                a = j % k; // modulus operator is inefficient;
            }
        }
        string1 = "hello" + "world"; // concatenation operator is inefficient
        string1.compareTo(string2); // compareTo is less energy efficient than string.equals

        return i;
    }
}