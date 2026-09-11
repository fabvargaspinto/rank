export const AuthProvider = {
    EMAIL: "EMAIL",
    GOOGLE: "GOOGLE",
} as const;

export type AuthProvider = (typeof AuthProvider)[keyof typeof AuthProvider];
