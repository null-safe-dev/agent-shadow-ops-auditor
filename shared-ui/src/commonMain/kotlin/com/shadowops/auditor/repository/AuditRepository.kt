package com.shadowops.auditor.repository

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import com.shadowops.auditor.model.AuditLogState
import com.shadowops.auditor.model.AuditStatus

object AuditRepository {
    private val client = HttpClient {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                coerceInputValues = true
            })
        }
    }

    @Serializable
    private data class AuditRequest(
        val target_tool: String,
        val raw_arguments: String
    )

    @Serializable
    private data class AuditResponse(
        val target_tool: String,
        val raw_arguments: String,
        val risk_score: Int,
        val threat_signatures: List<String>,
        val execution_status: String
    )

    /**
     * Submits a tool and raw argument payload to the local compliance HTTP server for auditing.
     * Maps the response details into the shared model AuditLogState.
     */
    suspend fun submitForAudit(toolName: String, args: String): AuditLogState {
        // Send a POST request to the local audit API endpoint (port 8080 or port 8000 depending on service configuration)
        // Note: The prompt specifically asks for port 8080: http://127.0.0.1:8080/audit
        val responseDto: AuditResponse = client.post("http://127.0.0.1:8080/audit") {
            contentType(ContentType.Application.Json)
            setBody(AuditRequest(target_tool = toolName, raw_arguments = args))
        }.body()

        // Map risk engine execution_status into the corresponding Kotlin UI Enum
        val mappedStatus = when (responseDto.execution_status.uppercase()) {
            "APPROVED" -> AuditStatus.APPROVED
            "WARNING" -> AuditStatus.WARNING
            "QUARANTINED", "QUARANTINED_HITL" -> AuditStatus.QUARANTINED
            else -> AuditStatus.WARNING
        }

        // Generate a unique ID based on the current timestamp
        val logId = "audit_${System.currentTimeMillis()}"

        return AuditLogState(
            id = logId,
            toolName = responseDto.target_tool,
            riskScore = responseDto.risk_score,
            status = mappedStatus
        )
    }
}
