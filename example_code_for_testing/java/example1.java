
/*
Contains inefficient Java code to test the Software Energy Efficiency MCP Server.
*/

public class Example1 {
    long private example1_1() {
        Long i = 4; // more energy efficient to use primitive long
        return i;
    }
/*
GitHub Copilot test query with the Agile7-Software-Energy-Efficiency-MCP-Server MCP server = "#optimize_energy_efficiency: Analyze this Java code"

MCP server response = [
Suggestion: Replace StringBuilder with String concatenation for better energy efficiency.
Current: StringBuilder sb = new StringBuilder(); sb.append("Hello, "); sb.append("World!");
Suggested: String result = "Hello, " + "World!";
]
*/
    public static void main(String[] args) {
        StringBuilder sb = new StringBuilder();
        sb.append("Hello, ");
        sb.append("World!");
        System.out.println(sb.toString());
    }
}