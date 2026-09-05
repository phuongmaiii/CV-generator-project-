package com.cvrecruitment.cv_recruitment_service.controller;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.mindrot.jbcrypt.BCrypt;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.validation.Valid;

import com.cvrecruitment.cv_recruitment_service.AccountRepository;
import com.cvrecruitment.cv_recruitment_service.AuthUtil;
import com.cvrecruitment.cv_recruitment_service.dto.RegisterRequest;
import com.cvrecruitment.cv_recruitment_service.dto.AccountResponse;
import com.cvrecruitment.cv_recruitment_service.entity.Account;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = {
    "http://localhost:5173", 
    "http://localhost:5174", 
    "https://cv-generator-project-umber.vercel.app"
}, allowCredentials = "true")
public class AuthController {

    private final AccountRepository accountRepository;
    private final AuthUtil authUtil;

    public AuthController(AccountRepository accountRepository, AuthUtil authUtil) {
        this.accountRepository = accountRepository;
        this.authUtil = authUtil;
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest request) {
        String email = request.getEmail().trim().toLowerCase();
        String role = request.getRole().trim().toUpperCase();
        if (!"CANDIDATE".equals(role) && !"HR".equals(role)) {
            return ResponseEntity.badRequest().body(Map.of("message", "Vai trò không hợp lệ"));
        }
        if (accountRepository.findByEmail(email).isPresent()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("message", "Email đã tồn tại"));
        }

        Account newAccount = new Account();
        newAccount.setEmail(email);
        newAccount.setPassword(BCrypt.hashpw(request.getPassword(), BCrypt.gensalt()));
        newAccount.setRole(role);

        if ("CANDIDATE".equals(role)) {
            newAccount.setFullName(request.getFullName());
        } else {
            String companyName = request.getCompanyName();
            if (companyName == null || companyName.isBlank()) {
                return ResponseEntity.badRequest().body(Map.of("message", "HR phải chọn công ty"));
            }
            
            // XÁC THỰC TÊN MIỀN BẢO MẬT HR
            Map<String, String> companyDomains = new HashMap<>();
            companyDomains.put("FPT Software", "@fpt.com.vn");
            companyDomains.put("Viettel Group", "@viettel.com.vn");
            companyDomains.put("VNG Corporation", "@vng.com.vn");
            companyDomains.put("Shopee Vietnam", "@shopee.com");
            // Thêm các domain công ty khác vào đây

            String expectedDomain = companyDomains.get(companyName);
            if (expectedDomain != null && !email.endsWith(expectedDomain)) {
                return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("message", "Đăng ký từ chối: HR của " + companyName + " bắt buộc phải sử dụng email đuôi " + expectedDomain));
            }

            newAccount.setCompanyName(companyName);
            newAccount.setFullName(request.getFullName());
        }

        String token = UUID.randomUUID().toString();
        newAccount.setToken(token);
        newAccount.setTokenIssuedAt(java.time.LocalDateTime.now());
        
        accountRepository.save(newAccount);

        Map<String, Object> res = new HashMap<>();
        res.put("token", token);
        res.put("role", role);
        res.put("accountId", newAccount.getId());
        res.put("email", email);
        res.put("fullName", newAccount.getFullName());
        return ResponseEntity.ok(res);
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody Map<String, String> payload) {
        String email = payload.get("email");
        String password = payload.get("password");

        if (email == null || password == null || email.isBlank() || password.isBlank()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "Sai email hoặc mật khẩu"));
        }
        email = email.trim().toLowerCase();

        Optional<Account> accOpt = accountRepository.findByEmail(email);
        if (accOpt.isEmpty() || !BCrypt.checkpw(password, accOpt.get().getPassword())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("message", "Sai email hoặc mật khẩu"));
        }

        Account account = accOpt.get();
        String token = UUID.randomUUID().toString();
        account.setToken(token);
        account.setTokenIssuedAt(java.time.LocalDateTime.now());
        accountRepository.save(account);

        Map<String, Object> res = new HashMap<>();
        res.put("token", token);
        res.put("role", account.getRole());
        res.put("accountId", account.getId());
        res.put("email", email);
        res.put("fullName", account.getFullName());
        res.put("companyName", account.getCompanyName());
        return ResponseEntity.ok(res);
    }

    @GetMapping("/me")
    public ResponseEntity<?> getMe(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        // Dùng chung AuthUtil (có kiểm tra hạn token) thay vì tự tra token riêng ở đây
        // như trước — trước đây /me không hề kiểm tra hạn, chỉ CandidateController/
        // JobPostingController có bản verifyToken riêng (cũng không kiểm tra hạn).
        Account account = authUtil.verifyToken(authHeader);
        if (account == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        return ResponseEntity.ok(AccountResponse.from(account));
    }
}
