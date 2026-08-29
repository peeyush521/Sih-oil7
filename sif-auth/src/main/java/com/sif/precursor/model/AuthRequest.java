package com.sif.precursor.model;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class AuthRequest {

    public record Register(
        @NotBlank @Email String email,
        @NotBlank @Size(min = 8, max = 128) String password,
        @NotBlank String fullName,
        String role,
        String plant
    ) {}

    public record Login(
        @NotBlank @Email String email,
        @NotBlank String password
    ) {}
}
