import java.util.Scanner;

public class BubbleSort {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter n: ");
        int n = sc.nextInt();

        int[] a = new int[n];
        System.out.print("Enter " + n + " integers: ");
        for (int i = 0; i < n; i++) {
            a[i] = sc.nextInt();
        }

        int swaps = 0;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - 1 - i; j++) {
                if (a[j] > a[j + 1]) {
                    int temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;
                    swaps++;
                }
            }
        }

        System.out.print("Sorted array: ");
        for (int i = 0; i < n; i++) {
            System.out.print(a[i] + " ");
        }
        System.out.println();
        System.out.println("Number of swaps: " + swaps);
    }
}
