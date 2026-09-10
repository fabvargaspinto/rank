export const AuthOauthProvider = {
    GOOGLE: "GOOGLE",
} as const;

export type AuthOauthProvider =
    (typeof AuthOauthProvider)[keyof typeof AuthOauthProvider];
