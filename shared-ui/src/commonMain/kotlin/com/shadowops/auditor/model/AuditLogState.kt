package com.shadowops.auditor.model

enum class AuditStatus {
    APPROVED,
    WARNING,
    QUARANTINED
}

data class AuditLogState(
    val id: String,
    val toolName: String,
    val riskScore: Int,
    val status: AuditStatus
)
