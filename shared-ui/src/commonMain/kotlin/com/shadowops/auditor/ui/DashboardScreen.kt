package com.shadowops.auditor.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shadowops.auditor.model.AuditLogState
import com.shadowops.auditor.model.AuditStatus

// Premium tailored theme colors
private val EmeraldGreen = Color(0xFF10B981)
private val CrimsonRed = Color(0xFFDC2626)
private val AmberOrange = Color(0xFFF59E0B)
private val SurfaceDark = Color(0xFF1F2937)
private val TextWhite = Color(0xFFF9FAFB)
private val BackgroundDark = Color(0xFF111827)

@Composable
fun DashboardScreen(
    logs: List<AuditLogState>,
    onApproveRelease: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    // State to simulate real-time updates of local mock callback clicks
    var activeLogs by remember(logs) { mutableStateOf(logs) }

    val totalBlocked = activeLogs.count { it.status == AuditStatus.QUARANTINED }
    val totalApproved = activeLogs.count { it.status == AuditStatus.APPROVED }
    val totalWarnings = activeLogs.count { it.status == AuditStatus.WARNING }

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp)
    ) {
        // Dashboard Title Header
        Text(
            text = "Compliance Pipeline Dashboard",
            color = TextWhite,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // Top Metric Bar Row
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            MetricCard(
                title = "Total Threats Blocked",
                value = totalBlocked.toString(),
                color = CrimsonRed,
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                title = "Warnings Raised",
                value = totalWarnings.toString(),
                color = AmberOrange,
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                title = "Approved Actions",
                value = totalApproved.toString(),
                color = EmeraldGreen,
                modifier = Modifier.weight(1f)
            )
        }

        Text(
            text = "Audit Activity Stream",
            color = TextWhite,
            fontSize = 18.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(bottom = 8.dp)
        )

        // Lazy column displaying individual audit cards
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            items(activeLogs, key = { it.id }) { log ->
                AuditLogCard(
                    log = log,
                    onApproveRelease = { logId ->
                        // Execute caller trigger
                        onApproveRelease(logId)
                        // Mock local UI state release state transition
                        activeLogs = activeLogs.map {
                            if (it.id == logId) it.copy(status = AuditStatus.APPROVED) else it
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp),
        modifier = modifier
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = title,
                color = TextWhite.copy(alpha = 0.7f),
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium
            )
            Text(
                text = value,
                color = color,
                fontSize = 28.sp,
                fontWeight = FontWeight.ExtraBold
            )
        }
    }
}

@Composable
fun AuditLogCard(
    log: AuditLogState,
    onApproveRelease: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    // Dynamic background selection: Emerald green for APPROVED, Crimson red for QUARANTINED, Amber for WARNING
    val cardColor = when (log.status) {
        AuditStatus.APPROVED -> EmeraldGreen
        AuditStatus.QUARANTINED -> CrimsonRed
        AuditStatus.WARNING -> AmberOrange
    }

    Card(
        colors = CardDefaults.cardColors(containerColor = SurfaceDark),
        shape = RoundedCornerShape(12.dp),
        modifier = modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Left Status Indicator Color Bar
            Box(
                modifier = Modifier
                    .width(6.dp)
                    .height(60.dp)
                    .background(cardColor, shape = RoundedCornerShape(4.dp))
            )

            Spacer(modifier = Modifier.width(12.dp))

            // Text Metadata Block
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = log.toolName,
                        color = TextWhite,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = "Risk: ${log.riskScore}",
                        color = TextWhite.copy(alpha = 0.8f),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
                
                Text(
                    text = "ID: ${log.id}",
                    color = TextWhite.copy(alpha = 0.5f),
                    fontSize = 11.sp
                )
                
                Text(
                    text = "STATUS: ${log.status.name}",
                    color = cardColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.ExtraBold
                )
            }

            // Right interactive area for quarantine approval callback action button
            if (log.status == AuditStatus.QUARANTINED) {
                Spacer(modifier = Modifier.width(8.dp))
                Button(
                    onClick = { onApproveRelease(log.id) },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = CrimsonRed,
                        contentColor = TextWhite
                    ),
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Text(
                        text = "Approve Release",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }
    }
}
