import java.math.BigInteger;

public class problem25{
    public static void main(String[] args){
        Boolean notfound = true;
        BigInteger[] terms =  {BigInteger.ONE,BigInteger.ONE};
        int index = 2;
        while (notfound) {
            index++;
            BigInteger next_term = terms[0].add(terms[1]);
            int length = integer_length(next_term);
            
            if (length == 1000){
                System.out.println(index);
                notfound = false;
            }
            else{
                terms[0] = terms[1];
                terms[1] = next_term;
            }

        }
        
    }
    public static int integer_length(BigInteger number){
        int length = (number.toString()).length();
        return length;

    }
}