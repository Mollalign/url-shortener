/**
 * Zod validators — frontend complement to backend Pydantic rules.
 *
 * These mirror the backend constraints exactly:
 *  - email: EmailStr
 *  - username: 3-50 chars, [a-zA-Z0-9_-]
 *  - password: 8-128, must have uppercase + digit
 *  - long_url: http/https only, must have domain
 *  - custom_alias: 3-50 chars, [a-zA-Z0-9_-]
 */
import { z } from "zod";

export const registerSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  username: z
    .string()
    .min(3, "Username must be at least 3 characters.")
    .max(50, "Username must be at most 50 characters.")
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      "Username may only contain letters, digits, hyphens, and underscores."
    ),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters.")
    .max(128, "Password must be at most 128 characters.")
    .refine((v) => /[A-Z]/.test(v), {
      message: "Password must contain at least one uppercase letter.",
    })
    .refine((v) => /[0-9]/.test(v), {
      message: "Password must contain at least one digit.",
    }),
});

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});

export const updateProfileSchema = z
  .object({
    username: z
      .string()
      .min(3)
      .max(50)
      .regex(/^[a-zA-Z0-9_-]+$/)
      .optional()
      .or(z.literal("")),
    password: z.string().min(8).max(128).optional().or(z.literal("")),
  })
  .refine((d) => d.username || d.password, {
    message: "Provide at least a new username or password.",
  });

export const createUrlSchema = z.object({
  long_url: z
    .string()
    .url("Enter a valid URL.")
    .refine(
      (v) => v.startsWith("http://") || v.startsWith("https://"),
      "Only http and https URLs are allowed."
    ),
  custom_alias: z
    .string()
    .min(3, "Alias must be at least 3 characters.")
    .max(50, "Alias must be at most 50 characters.")
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      "Alias may only contain letters, digits, hyphens, and underscores."
    )
    .optional()
    .or(z.literal("")),
  expiration_date: z.string().optional().or(z.literal("")),
});

export type RegisterFormValues = z.infer<typeof registerSchema>;
export type LoginFormValues = z.infer<typeof loginSchema>;
export type UpdateProfileFormValues = z.infer<typeof updateProfileSchema>;
export type CreateUrlFormValues = z.infer<typeof createUrlSchema>;
