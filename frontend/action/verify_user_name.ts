

export async function verifyUserName(name: string) {

    
   
 const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/verify-user-name`, {
    method: 'POST',
    body: JSON.stringify({ name }),
 });

 return response.json();

}