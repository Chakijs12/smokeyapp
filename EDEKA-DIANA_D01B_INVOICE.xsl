
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:date="http://exslt.org/dates-and-times" xmlns:exsl="http://exslt.org/common" extension-element-prefixes="date exsl">
	<xsl:import href="EDIFACT-xml2edi.xsl"/>
	<xsl:output method="text" indent="yes" encoding="utf-8"/>

	<!--Made By Andris Kopmanis|Edisoft Latvia SIA|02.07.2020|-->

	<xsl:variable name="currency" select="normalize-space(Document-Invoice/Invoice-Header/InvoiceCurrency)"/>
	<xsl:variable name="remarks" select="normalize-space(Document-Invoice/Invoice-Header/Remarks)"/>
	<!-- Root template -->
	<xsl:template match="/">
		<!-- Transform the document (to a set of 'segment' elements) -->
		<xsl:variable name="processed_doc_tmp">
			<xsl:apply-templates mode="interchange" select="/Document-Invoice"/>
		</xsl:variable>
		<!-- Now transform 'segment' elements to EDIFACT segments -->
		<xsl:apply-templates select="exsl:node-set($processed_doc_tmp)/child::*"/>
	</xsl:template>
	<!-- Invoice -->

	<xsl:template mode="interchange" match="Document-Invoice">
		<!-- Process the document -->
		<xsl:variable name="processed_doc_tmp">
			<xsl:apply-templates mode="message" select="."/>
		</xsl:variable>
		<xsl:variable name="processed_doc" select="exsl:node-set($processed_doc_tmp)"/>


		<!--PTG Management and OTHERS D01B Format Abroad partners-->

		<!-- The interchange envelope (begin) -->
		<!-- UNA -->
		<!--<segment tag="UNA"/>-->
		<!-- UNB -->
		<segment tag="UNB">
			<element>
				<subelement>
					<xsl:text>UNOC</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>3</xsl:text>
				</subelement>
			</element>
			<element>
				<!-- Sender -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/ILN)"/>
				</subelement>
				<subelement>
					<!-- 14 ICS (ILN) -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>14</xsl:text>
				</subelement>
			</element>
			<element>
				<!-- Receiver -->
				<subelement>
					<xsl:value-of select="normalize-space(Document-Parties/Receiver/ILN)"/>
				</subelement>
				<subelement>
					<!-- 14 ICS (ILN) -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>14</xsl:text>
				</subelement>
			</element>
			<element>
				<!-- Date -->
				<xsl:value-of select="translate(substring(date:date-time(), 3, 14), 'T-:', ':')"/>
			</element>
			<element>
				<!-- Doc nr -->
				<xsl:value-of select="normalize-space(Invoice-Header/InvoiceNumber)"/>
			</element>
			<element>
			</element>
			<element>

				<!--INVMAT_V2 - When the paper invoice should be considered as the official invoice format (Paper | EDI)-->
				<!--<subelement>
					<xsl:text>INVMAT_V2</xsl:text>
				</subelement>-->

				<!--INVDMT_V2 - When it concerns a dematerialized, electronic invoice (EDI)-->
				<subelement>
					<xsl:text>INVDMT_V2</xsl:text>
				</subelement>
			</element>
			<element>
			</element>
			<element/>
			<!--<element>
				<subelement>
					<xsl:text>EANCOM</xsl:text>
				</subelement>
			</element>-->
		</segment>
		<!-- Main content (has only the beginning of the message envelope) -->
		<xsl:copy-of select="$processed_doc"/>
		<segment tag="UNH">
			<element>

				<xsl:value-of select="'3'"/>
			</element>
			<element>
				<subelement>
					<xsl:text>INVOIC</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>D</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>01B</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>UN</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>EAN010</xsl:text>
				</subelement>
			</element>
		</segment>
		<segment tag="BGM">
			<!-- C002  DOCUMENT/MESSAGE NAME (C) -->
			<element>
				<!-- 1001   Document/message name, coded (C  an..3) -->
				<subelement>
					<xsl:text>393</xsl:text>

					<!-- 388 Tax invoice,  380 Commercial Invoice -->
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement/>
				<!-- 1000   Document/message name (C  an..35) -->
				<!-- E.g., INVOIC -->
				<subelement/>
			</element>
			<!-- 1004  DOCUMENT/MESSAGE NUMBER (C  an..35) -->
			<element>
				<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
			</element>
			<!-- 1225  MESSAGE FUNCTION, CODED (C  an..3) -->
			<element>
				<xsl:text>9</xsl:text>
				<!-- 9 Original -->
			</element>
			<!-- 4343  RESPONSE TYPE, CODED (C  an..3) -->
			<!-- AB Message acknowledgement, NA No acknowledgement needed -->
			<element/>
		</segment>
		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>137</xsl:text>
					<!-- 325 Tax period  	Period a tax rate/tax amount etc. is applicable. 	
GS1 Description: A period which is designated by tax authorities, e.g. VAT period. -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>

					<!-- Original value of EDIFACT D01B |Andris Kopmanis|-->

					<!--<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>-->

					<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>


		<!-- RFF REFERENCE -->
		<segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>CT</xsl:text>
					<!-- ON Order number (purchase) -->
				</subelement>
				<subelement>
					<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
				</subelement>
			</element>
		</segment>

		<!-- Segment group 2: NAD-LOC-FII-SG3-SG4-SG5 -->
		<!-- NAD NAME AND ADDRESS -->
		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>SU</xsl:text>
				<!-- SE Seller -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
		</segment>

		<!-- NAD NAME AND ADDRESS -->
		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>CPE</xsl:text>
				<!-- BY Buyer -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Document-Parties/Receiver/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
		</segment>

		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>PR</xsl:text>
				<!--  	Ordered by Party who issued an order. -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="Invoice-Parties/Payer/ILN"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<element/>
		</segment>

		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>PE</xsl:text>
				<!--  	Ordered by Party who issued an order. -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<element/>
		</segment>

		<!-- Tax-Summary-Line -->
		<segment tag="TAX">
			<!-- 5283  DUTY/TAX/FEE FUNCTION QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>7</xsl:text>
				<!-- 7 Tax -->
			</element>
			<!-- C241  DUTY/TAX/FEE TYPE (C) -->
			<element>
				<!-- 5153   Duty/tax/fee type, coded (C  an..3) -->
				<subelement>
					<xsl:text>VAT</xsl:text>
					<!-- VAT -->
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<!-- 5152   Duty/tax/fee type (C  an..35) -->
			</element>
			<!-- C533  DUTY/TAX/FEE ACCOUNT DETAIL -->
			<element/>
			<!-- 5286  DUTY/TAX/FEE ASSESSMENT BASIS (C  an..15) -->
			<element>
				<!--<xsl:value-of select="format-number(Invoice-Summary/Tax-Summary/Tax-Summary-Line/TaxableAmount, '0.00')"/>-->
			</element>

			<element>

				<subelement>
				</subelement>

				<subelement>
				</subelement>
				<subelement>
				</subelement>
				<subelement>
					<xsl:text>7</xsl:text>
				</subelement>
			</element>
			<element>
				<xsl:text>S</xsl:text>
			</element>
		</segment>


		<!-- NAD NAME AND ADDRESS -->
		<segment tag="CUX">
			<!-- C504  CURRENCY DETAILS (C) -->
			<element>
				<!-- 6347   Currency details qualifier (M  an..3) -->
				<subelement>
					<xsl:text>2</xsl:text>
					<!-- 2 Reference currency -->
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement>
					<!--				<xsl:choose>
					<xsl:when test="$currency='CZK'">
						<xsl:value-of select="''"/>
					</xsl:when>
					<xsl:otherwise>-->
					<xsl:value-of select="$currency"/>
					<!--					</xsl:otherwise>
				</xsl:choose>-->
				</subelement>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement>
					<xsl:text>4</xsl:text>
					<!-- 4 Invoicing currency -->
				</subelement>
				<!-- 6348   Currency rate base (C  n..4) -->
				<subelement/>
			</element>
		</segment>

		<!--Processes Invoice Lines-->
		<xsl:apply-templates select="Invoice-Lines/Line/Line-Item"/>
		<!-- Summary section -->
		<!--UNS Section control-->
		<segment tag="UNS">
			<!--0081  SECTION IDENTIFICATION (M  a1)-->
			<element>
				<xsl:text>S</xsl:text>
			</element>
		</segment>


		<segment tag="MOA">
			<element>
				<subelement>
					<xsl:text>86</xsl:text>
				</subelement>
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/TotalNetAmount, '0.00')"/>
				</subelement>
				<subelement/>
				<subelement/>
				<subelement/>
			</element>
		</segment>

		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>124</xsl:text>
					<!-- 79 Total line items amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/TotalTaxAmount, '0.00')"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>125</xsl:text>
					<!-- 79 Total line items amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="Invoice-Summary/TotalNetAmount"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>9</xsl:text>
					<!-- 125 Taxable amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="Invoice-Summary/TotalNetAmount"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<segment tag="UNT">
			<element>
				<!-- Number of segments between UNH and UNT (inclusive) -->
				<xsl:value-of select="count($processed_doc/segment) + 2"/>
				<!-- Or: count($processed_doc/child::*) + 1 -->
			</element>
			<element>
				<!-- Sender's unique message reference (OrderNumber) -->
				<!-- xsl:value-of select="normalize-space(Order-Header/OrderNumber)"  -->
				<xsl:value-of select="'3'"/>
			</element>
		</segment>
		<segment tag="UNZ">
			<element>
				<xsl:value-of select="'2'"/>
			</element>
			<element>
				<!-- Number of messages or functional groups (if present) -->
				<xsl:value-of select="normalize-space(Invoice-Header/InvoiceNumber)"/>
			</element>
		</segment>
	</xsl:template>
	<!-- Invoice -->
	<xsl:template mode="message" match="Document-Invoice">
		<!-- Process the document -->
		<xsl:variable name="processed_doc_tmp">
			<xsl:apply-templates mode="segments" select="."/>
		</xsl:variable>
		<xsl:variable name="processed_doc" select="exsl:node-set($processed_doc_tmp)"/>


		<!--PTG Management and OTHERS D01B Format Abroad partners-->
		<!-- Message envelope (begin) -->
		<!-- UNH Message header -->
		<segment tag="UNH">
			<element>
				<!-- Sender's unique message reference (OrderNumber) -->
				<!-- xsl:value-of select="normalize-space(Order-Header/OrderNumber)"  -->
				<xsl:value-of select="position()"/>
			</element>
			<element>
				<subelement>
					<xsl:text>INVOIC</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>D</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>01B</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>UN</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>EAN011</xsl:text>
				</subelement>
			</element>
		</segment>
		<!-- Main content (has only the beginning of the message envelope) -->
		<xsl:copy-of select="$processed_doc"/>
		<!-- Message envelope (end) -->
		<!-- UNT Message trailer -->
		<segment tag="UNT">
			<element>
				<!-- Number of segments between UNH and UNT (inclusive) -->
				<xsl:value-of select="count($processed_doc/segment) + 2"/>
				<!-- Or: count($processed_doc/child::*) + 1 -->
			</element>
			<element>
				<!-- Sender's unique message reference (OrderNumber) -->
				<!-- xsl:value-of select="normalize-space(Order-Header/OrderNumber)"  -->
				<xsl:value-of select="position()"/>
			</element>
		</segment>
	</xsl:template>

	<!-- Invoice -->
	<xsl:template mode="segments" match="Document-Invoice">
		<!--PTG Management and OTHERS D01B Format Abroad partners-->
		<!-- Header -->
		<!-- BGM BEGINNING OF MESSAGE -->
		<segment tag="BGM">
			<!-- C002  DOCUMENT/MESSAGE NAME (C) -->
			<element>
				<!-- 1001   Document/message name, coded (C  an..3) -->
				<subelement>
					<xsl:choose>
						<xsl:when test="not(Invoice-Header/DocumentNameCode)">
							<xsl:text>380</xsl:text>
						</xsl:when>
						<xsl:when test="Invoice-Header/DocumentNameCode = 380">
							<xsl:text>380</xsl:text>
						</xsl:when>
						<xsl:when test="Invoice-Header/DocumentNameCode = 381">
							<xsl:text>381</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="Invoice-Header/DocumentNameCode"/>
						</xsl:otherwise>
					</xsl:choose>

					<!-- 388 Tax invoice,  380 Commercial Invoice -->
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement/>
				<!-- 1000   Document/message name (C  an..35) -->
				<!-- E.g., INVOIC -->
				<subelement/>
			</element>
			<!-- 1004  DOCUMENT/MESSAGE NUMBER (C  an..35) -->
			<element>
				<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
			</element>
			<!-- 1225  MESSAGE FUNCTION, CODED (C  an..3) -->
			<element>
				<xsl:text>9</xsl:text>
				<!-- 9 Original -->
			</element>
			<!-- 4343  RESPONSE TYPE, CODED (C  an..3) -->
			<!-- AB Message acknowledgement, NA No acknowledgement needed -->
			<element/>
		</segment>

		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>137</xsl:text>
					<!-- 325 Tax period  	Period a tax rate/tax amount etc. is applicable. 	
GS1 Description: A period which is designated by tax authorities, e.g. VAT period. -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>

					<!-- Original value of EDIFACT D01B |Andris Kopmanis|-->

					<!--<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>-->

					<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>

		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>35</xsl:text>
					<!-- 35 Delivery date/time -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>
					<xsl:value-of select="translate(normalize-space(Invoice-Header/Delivery/DeliveryDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>

		<!-- DTM DATE/TIME/PERIOD -->
		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>69</xsl:text>
					<!-- 137 Document/message date/time -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>
					<xsl:value-of select="translate(normalize-space(Invoice-Header/InvoiceDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>


		<!--No need for Segment PAI for Harminozed EDIFACT D01B version | Andris Kopmanis|-->

		<!--<Segment group 1: RFF-DTM>
		<This segment allows the party issuing the Invoice to specify how they would like payment to be made.>
		<segment tag="PAI">
			<element>
				<subelement/>
				<subelement/>
				<subelement>
					<xsl:text>42</xsl:text>
					< =  Payment to bank account>
				</subelement>
			</element>
		</segment>-->

		<!--No need for Segment ALI for Harminozed EDIFACT D01B version | Andris Kopmanis|-->

		<!--<segment tag="ALI">
			<element>
				<subelement>
					<xsl:text>CZ</xsl:text>
				</subelement>
			</element>
			<element/>
			<element>
				<subelement>
					<xsl:text>141</xsl:text>
				</subelement>
			</element>
		</segment>-->

		<segment tag="FTX">
			<element>
				<subelement>
					<xsl:text>AAK</xsl:text>
				</subelement>
			</element>
			<element>
			</element>
			<element>
				<subelement>
					<xsl:text>ST1</xsl:text>
				</subelement>
			</element>
			<element>
			</element>
			<element>
				<subelement>
					<xsl:text>DE</xsl:text>
				</subelement>
			</element>
		</segment>


		<segment tag="FTX">
			<element>
				<subelement>
					<xsl:text>ABN</xsl:text>
				</subelement>
			</element>
			<element>
				<subelement>
					<xsl:text>1</xsl:text>
				</subelement>
			</element>
			<element>
				<subelement>
					<xsl:text>BA</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>LEI</xsl:text>
				</subelement>
				<subelement>
					<xsl:text>246</xsl:text>
				</subelement>
			</element>
		</segment>

		<!-- AAK Despatch Number -->
		<segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>DQ</xsl:text>
				</subelement>
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Header/Delivery/DespatchNumber)"/>
				</subelement>
			</element>
		</segment>

		<!-- DTM DATE/TIME/PERIOD -->
		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>171</xsl:text>
					<!-- 171 Reference date/time -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>
					<xsl:value-of select="translate(normalize-space(Invoice-Header/Delivery/DeliveryDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>

		<!-- RFF REFERENCE -->
		<segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>ON</xsl:text>
					<!-- ON Order number (purchase) -->
				</subelement>
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Header/Order/BuyerOrderNumber)"/>
				</subelement>
			</element>
		</segment>

		<segment tag="DTM">
			<!-- C507  DATE/TIME/PERIOD (M) -->
			<element>
				<!-- 2005   Date/time/period qualifier (M  an..3) -->
				<subelement>
					<xsl:text>171</xsl:text>
					<!-- 171 Reference date/time -->
				</subelement>
				<!-- 2380   Date/time/period (C  an..35) -->
				<subelement>
					<xsl:value-of select="translate(normalize-space(Invoice-Header/Delivery/DeliveryDate), '-', '')"/>
				</subelement>
				<!-- 2379   Date/time/period format qualifier (C  an..3) -->
				<subelement>
					<xsl:text>102</xsl:text>
					<!-- Date/time/period format qualifier: CCYYMMDD -->
				</subelement>
			</element>
		</segment>

		<!-- RFF REFERENCE -->
		<segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>ABO</xsl:text>
					<!-- ON Order number (purchase) -->
				</subelement>
				<subelement>
					<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
					<!--<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/><!-->
				</subelement>
			</element>
		</segment>

		<xsl:if test="normalize-space(Invoice-Header/Order/BuyerOrderDate)">
			<!-- DTM DATE/TIME/PERIOD -->
			<segment tag="DTM">
				<!-- C507  DATE/TIME/PERIOD (M) -->
				<element>
					<!-- 2005   Date/time/period qualifier (M  an..3) -->
					<subelement>
						<xsl:text>171</xsl:text>
						<!-- 171 Reference date/time -->
					</subelement>
					<!-- 2380   Date/time/period (C  an..35) -->
					<subelement>
						<xsl:value-of select="translate(normalize-space(Invoice-Header/Order/BuyerOrderDate), '-', '')"/>
					</subelement>
					<!-- 2379   Date/time/period format qualifier (C  an..3) -->
					<subelement>
						<xsl:text>102</xsl:text>
						<!-- Date/time/period format qualifier: CCYYMMDD -->
					</subelement>
				</element>
			</segment>
		</xsl:if>

		<!-- RFF REFERENCE -->
		<segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>CT</xsl:text>
					<!-- ON Order number (purchase) -->
				</subelement>
				<subelement>
					<xsl:value-of select="substring(normalize-space(Invoice-Header/InvoiceNumber), 1, 35)"/>
				</subelement>
			</element>
		</segment>

		<!-- Segment group 2: NAD-LOC-FII-SG3-SG4-SG5 -->
		<!-- NAD NAME AND ADDRESS -->
		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>SU</xsl:text>
				<!-- SE Seller -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<!-- C058  NAME AND ADDRESS (C) -->
			<element/>
			<!-- C080  PARTY NAME (C) -->
			<element>
				<!-- 3036   Party name (M  an..35) -->
				<!-- 3036   Party name (C  an..35) * 4 -->
				<xsl:call-template name="escaped_string_to_parts">
					<xsl:with-param name="str" select="normalize-space(Invoice-Parties/Seller/Name)"/>
					<xsl:with-param name="part_length" select="35"/>
					<xsl:with-param name="max_parts" select="5"/>
				</xsl:call-template>
				<!-- 3045   Party name format, coded (C  an..3) -->
				<subelement/>
			</element>
			<!-- C059  STREET (C) -->
			<element>
				<xsl:value-of select="translate(Invoice-Parties/Seller/StreetAndNumber, translate(Invoice-Parties/Seller/StreetAndNumber, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.', ''), '')"/>
			</element>
			<!-- 3164  CITY NAME (C  an..35) -->
			<element>
				<xsl:value-of select="translate(Invoice-Parties/Seller/CityName, translate(Invoice-Parties/Seller/CityName, 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.', ''), '')"/>
			</element>
			<element>
				<!-- 3229  COUNTRY SUB-ENTITY IDENTIFICATION (C  an..9) -->
			</element>
			<!-- 3251  POSTCODE IDENTIFICATION (C  an..9) -->
			<element>
				<xsl:value-of select="normalize-space(Invoice-Parties/Seller/PostalCode)"/>
			</element>
			<!-- 3207  COUNTRY, CODED (C  an..3) -->
			<element>
				<xsl:value-of select="normalize-space(Invoice-Parties/Seller/Country)"/>
			</element>
		</segment>

		<segment tag="RFF">
			<!-- C506  REFERENCE (M) -->
			<element>
				<!-- 1153   Reference qualifier (M  an..3) -->
				<subelement>
					<xsl:text>FC</xsl:text>
					<!-- FC Fiscal number (Tax payer's number) -->
				</subelement>
				<!-- 1154   Reference number (C  an..35) -->
				<subelement>
					<xsl:value-of select="substring(normalize-space(Invoice-Parties/Seller/TaxID),3,15)"/>
				</subelement>
				<!-- 1156   Line number (C  an..6) -->
				<!-- 4000   Reference version number (C  an..35) -->
			</element>
		</segment>

		<segment tag="RFF">
			<!-- C506  REFERENCE (M) -->
			<element>
				<!-- 1153   Reference qualifier (M  an..3) -->
				<subelement>
					<xsl:text>VA</xsl:text>
					<!-- FC Fiscal number (Tax payer's number) -->
				</subelement>
				<!-- 1154   Reference number (C  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Seller/TaxID)"/>
				</subelement>
				<!-- 1156   Line number (C  an..6) -->
				<!-- 4000   Reference version number (C  an..35) -->
			</element>
		</segment>


		<!-- NAD NAME AND ADDRESS -->
		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>BY</xsl:text>
				<!-- BY Buyer -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(Invoice-Parties/Buyer/ILN)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<!-- C058  NAME AND ADDRESS (C) -->
			<element/>
			<!-- C080  PARTY NAME (C) -->
			<element>
				<subelement>
					<!-- 3036   Party name (M  an..35) -->
					<!-- 3036   Party name (C  an..35) * 4 -->

					<xsl:call-template name="escaped_string_to_parts">
						<xsl:with-param name="str" select="normalize-space(Invoice-Parties/Buyer/Name)"/>
						<xsl:with-param name="part_length" select="35"/>
						<xsl:with-param name="max_parts" select="5"/>
					</xsl:call-template>
					<!-- 3045   Party name format, coded (C  an..3) -->
				</subelement>
			</element>
			<!-- C059  STREET (C) -->
			<element>
				<xsl:value-of select="normalize-space(Invoice-Parties/Buyer/StreetAndNumber)"/>
			</element>
			<!-- 3164  CITY NAME (C  an..35) -->
			<element>
				<xsl:value-of select="normalize-space(Invoice-Parties/Buyer/CityName)"/>
			</element>
			<element>
				<!-- 3229  COUNTRY SUB-ENTITY IDENTIFICATION (C  an..9) -->
			</element>
			<!-- 3251  POSTCODE IDENTIFICATION (C  an..9) -->
			<element>
				<xsl:value-of select="normalize-space(Invoice-Parties/Buyer/PostalCode)"/>
			</element>
			<!-- 3207  COUNTRY, CODED (C  an..3) -->
			<element>
				<xsl:value-of select="normalize-space(Invoice-Parties/Buyer/Country)"/>
			</element>
		</segment>

		<segment tag="NAD">
			<!-- 3035  PARTY QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>DP</xsl:text>
				<!--  	Ordered by Party who issued an order. -->
			</element>
			<!-- C082  PARTY IDENTIFICATION DETAILS (C) -->
			<element>
				<!-- 3039   Party id. identification (M  an..35) -->
				<subelement>
					<xsl:value-of select="normalize-space(//DeliveryLocationNumber)"/>
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<subelement/>
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<subelement>
					<!--  9 EAN -->
					<!-- 91 Assigned by seller or seller's agent -->
					<!-- 92 Assigned by buyer or buyer's agent -->
					<xsl:text>9</xsl:text>
				</subelement>
			</element>
			<element/>
			<element>

				<!-- 3036   Party name (M  an..35) -->
				<!-- 3036   Party name (C  an..35) * 4 -->

				<xsl:call-template name="escaped_string_to_parts">
					<xsl:with-param name="str" select="normalize-space(Invoice-Header/Delivery/Name)"/>
					<xsl:with-param name="part_length" select="35"/>
					<xsl:with-param name="max_parts" select="5"/>
				</xsl:call-template>
				<!-- 3045   Party name format, coded (C  an..3) -->
				<subelement/>
			</element>
			<element>
				<xsl:value-of select="normalize-space(Invoice-Header/Delivery/StreetAndNumber)"/>
			</element>
			<element>
				<xsl:value-of select="normalize-space(Invoice-Header/Delivery/CityName)"/>
			</element>
			<element/>
			<element>
				<xsl:value-of select="normalize-space(Invoice-Header/Delivery/PostalCode)"/>
			</element>
			<element>
				<xsl:value-of select="normalize-space(Invoice-Header/Delivery/Country)"/>
			</element>
			<!-- C058  NAME AND ADDRESS (C) -->
		</segment>

		<!-- Tax-Summary-Line -->
		<segment tag="TAX">
			<!-- 5283  DUTY/TAX/FEE FUNCTION QUALIFIER (M  an..3) -->
			<element>
				<xsl:text>7</xsl:text>
				<!-- 7 Tax -->
			</element>
			<!-- C241  DUTY/TAX/FEE TYPE (C) -->
			<element>
				<!-- 5153   Duty/tax/fee type, coded (C  an..3) -->
				<subelement>
					<xsl:text>VAT</xsl:text>
					<!-- VAT -->
				</subelement>
				<!-- 1131   Code list qualifier (C  an..3) -->
				<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				<!-- 5152   Duty/tax/fee type (C  an..35) -->
			</element>
			<!-- C533  DUTY/TAX/FEE ACCOUNT DETAIL -->
			<element/>
			<!-- 5286  DUTY/TAX/FEE ASSESSMENT BASIS (C  an..15) -->
			<element>
				<!--<xsl:value-of select="format-number(Invoice-Summary/Tax-Summary/Tax-Summary-Line/TaxableAmount, '0.00')"/>-->
			</element>

			<element>

				<subelement>
				</subelement>

				<subelement>
				</subelement>
				<subelement>
				</subelement>
				<subelement>
					<xsl:text>7</xsl:text>
				</subelement>
			</element>
			<element>
				<xsl:text>S</xsl:text>
			</element>
		</segment>


		<!-- NAD NAME AND ADDRESS -->
		<segment tag="CUX">
			<!-- C504  CURRENCY DETAILS (C) -->
			<element>
				<!-- 6347   Currency details qualifier (M  an..3) -->
				<subelement>
					<xsl:text>2</xsl:text>
					<!-- 2 Reference currency -->
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement>
					<!--				<xsl:choose>
					<xsl:when test="$currency='CZK'">
						<xsl:value-of select="''"/>
					</xsl:when>
					<xsl:otherwise>-->
					<xsl:value-of select="$currency"/>
					<!--					</xsl:otherwise>
				</xsl:choose>-->
				</subelement>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement>
					<xsl:text>4</xsl:text>
					<!-- 4 Invoicing currency -->
				</subelement>
				<!-- 6348   Currency rate base (C  n..4) -->
				<subelement/>
			</element>
		</segment>

		<!--Processes Invoice Lines-->
		<xsl:apply-templates select="Invoice-Lines/Line/Line-Item"/>
		<!-- Summary section -->
		<!--UNS Section control-->
		<segment tag="UNS">
			<!--0081  SECTION IDENTIFICATION (M  a1)-->
			<element>
				<xsl:text>S</xsl:text>
			</element>
		</segment>

		<!--No need for Segment ALI for Harminozed EDIFACT D01B version | Andris Kopmanis|-->

		<!-- CNT Control total 
		<segment tag="CNT">
			 C270  CONTROL (M) 
			<element>
				 6069   Control qualifier (M  an..3) 
				<subelement>
					<xsl:text>2</xsl:text>
					 2 Number of line items in message 
				</subelement>
				 6066   Control value (M  n..18) 
				<subelement>
					<xsl:value-of select="number(Invoice-Summary/TotalLines)"/>
				</subelement>
				 6411   Measure unit qualifier (C  an..3) 
				<subelement/>
			</element>
		</segment>-->


		<segment tag="MOA">
			<element>
				<subelement>
					<xsl:text>77</xsl:text>
				</subelement>
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/TotalGrossAmount, '0.00')"/>
				</subelement>
				<subelement/>
				<subelement/>
				<subelement/>
			</element>
		</segment>

		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>79</xsl:text>
					<!-- 79 Total line items amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/TotalNetAmount, '0.00')"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>131</xsl:text>
					<!-- 79 Total line items amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="'0'"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>125</xsl:text>
					<!-- 125 Taxable amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="Invoice-Summary/TotalNetAmount - Invoice-Summary/TotalTaxAmount"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>
		<!--This segment transfers the amount which is to be paid as an advance payment-->
		<!--If a percentage of the advance payment is indicated, this segment is obligatory-->

		<!--This segment indicates the percentage of the incoiced amount which is the amount of the advance payment-->
		<!--If the percentage of the advance payment is indicated, the previous segment is mandatory-->

		<!--segment tag="RFF">
			<element>
				<subelement>
					<xsl:text>ZZZ</xsl:text>
				</subelement>
				<subelement>
					<xsl:value-of select="'0'"/>
				</subelement>
				<subelement/>
				<subelement/>
				<subelement/>
			</element>
		</segment-->

		<!--This segment transfers the amount which has already been paid as an advance payment-->

		<!--segment tag="MOA">
			<element>
				<subelement-->
		<!--prepaid amount-->
		<!--xsl:text>113</xsl:text>
				</subelement>
				<subelement-->
		<!--total advance amount paid-->
		<!--xsl:value-of select="'0'"/>
				</subelement>
				<subelement/>
				<subelement/>
				<subelement/>
			</element>
		</segment-->

		<!--This segment transfers the amount to be paid.-->
		<!--IF advance payments are not required, this amount is identical with the total invoiced amount-->

		<!--<segment tag="MOA">
			<element>
				<subelement>
					amount due/amount payable
					<xsl:text>9</xsl:text>
				</subelement>
				<subelement>
					to be paid (remaining amount to be paid)
					<xsl:value-of select="format-number(Invoice-Summary/TotalGrossAmount, '0.00')"/>
				</subelement>
				<subelement/>
				<subelement/>
				<subelement/>
			</element>
		</segment>-->


		<!-- MOA Monetary amount -->
		<segment tag="MOA">
			<!-- C516  MONETARY AMOUNT (M) -->
			<element>
				<!-- 5025   Monetary amount type qualifier (M  an..3) -->
				<subelement>
					<xsl:text>124</xsl:text>
					<!-- 124 Tax amount -->
				</subelement>
				<!-- 5004   Monetary amount (C  n..18) -->
				<subelement>
					<xsl:value-of select="format-number(Invoice-Summary/Tax-Summary/Tax-Summary-Line/TaxAmount, '0.00')"/>
				</subelement>
				<!-- 6345   Currency, coded (C  an..3) -->
				<subelement/>
				<!-- 6343   Currency qualifier (C  an..3) -->
				<subelement/>
				<!-- 4405   Status, coded (C  an..3) -->
				<subelement/>
			</element>
		</segment>

		<!-- MOA Monetary amount -->
		<xsl:if test="Invoice-Summary/IncreaseTotalTaxAmount">
			<segment tag="MOA">
				<!-- C516  MONETARY AMOUNT (M) -->
				<element>
					<!-- 5025   Monetary amount type qualifier (M  an..3) -->
					<subelement>
						<xsl:text>124</xsl:text>
						<!-- 124 Tax amount -->
					</subelement>
					<!-- 5004   Monetary amount (C  n..18) -->
					<subelement>
						<xsl:value-of select="format-number(Invoice-Summary/IncreaseTotalTaxAmount, '0.00')"/>
					</subelement>
					<!-- 6345   Currency, coded (C  an..3) -->
					<subelement/>
					<!-- 6343   Currency qualifier (C  an..3) -->
					<subelement/>
					<!-- 4405   Status, coded (C  an..3) -->
					<subelement/>
				</element>
			</segment>
		</xsl:if>
		<!-- MOA Monetary amount -->
		<xsl:if test="Invoice-Summary/DecreaseTotalTaxAmount">
			<segment tag="MOA">
				<!-- C516  MONETARY AMOUNT (M) -->
				<element>
					<!-- 5025   Monetary amount type qualifier (M  an..3) -->
					<subelement>
						<xsl:text>124</xsl:text>
						<!-- 124 Tax amount -->
					</subelement>
					<!-- 5004   Monetary amount (C  n..18) -->
					<subelement>
						<xsl:value-of select="format-number(Invoice-Summary/DecreaseTotalTaxAmount, '0.00')"/>
					</subelement>
					<!-- 6345   Currency, coded (C  an..3) -->
					<subelement/>
					<!-- 6343   Currency qualifier (C  an..3) -->
					<subelement/>
					<!-- 4405   Status, coded (C  an..3) -->
					<subelement/>
				</element>
			</segment>
		</xsl:if>

		<!-- Segment group 50:TAX-MOA -->
		<xsl:apply-templates select="Invoice-Summary/Tax-Summary/Tax-Summary-Line"/>
	</xsl:template>

	<!-- Invoice lines -->

	<xsl:template match="Invoice-Lines/Line/Line-Item">
		<!--D01B Format Abroad partners-->
		<!-- LIN Line item -->


		<xsl:if test="InvoiceUnitNetPrice &gt; 0">
			<segment tag="LIN">
				<!-- 1082  LINE ITEM NUMBER (C  n..6) -->
				<element>
					<xsl:value-of select="position()"/>
				</element>
				<!-- 1229  ACTION REQUEST/NOTIFICATION, CODED (C  an..3) -->
				<element/>
				<!-- C212  ITEM NUMBER IDENTIFICATION (C) -->
				<element>
					<!-- 7140   Item number (C  an..35) -->
					<xsl:if test="normalize-space(EAN)">
						<subelement>
							<!-- Item number identification -->
							<xsl:value-of select="normalize-space(EAN)"/>
						</subelement>

						<!-- 7143   Item number type, coded (C  an..3) -->
						<subelement>
							<xsl:text>SRV</xsl:text>
							<!-- SRV GS1 Global Trade Item Number -->
						</subelement>
					</xsl:if>
					<!-- 1131   Code list qualifier (C  an..3) -->
					<!-- 3055   Code list responsible agency, coded (C  an..3) -->
				</element>

				<!-- C829  SUB-LINE INFORMATION (C) -->
				<!-- 1222  CONFIGURATION LEVEL (C  n..2) -->
				<!-- 7083  CONFIGURATION, CODED (C  an..3) -->
			</segment>

			<xsl:if test="normalize-space(BuyerItemCode)">
				<!-- PIA Additional product id -->
				<segment tag="PIA">
					<!-- 4347  PRODUCT ID. FUNCTION QUALIFIER (M  an..3) -->
					<element>
						<xsl:text>1</xsl:text>
						<!-- 1  Additional identification -->
					</element>
					<!-- C212  ITEM NUMBER IDENTIFICATION (M) -->
					<element>
						<!-- 7140   Item number (C  an..35) -->
						<subelement>
							<xsl:value-of select="normalize-space(BuyerItemCode)"/>
						</subelement>
						<!-- 7143   Item number type, coded (C  an..3) -->
						<subelement>
							<xsl:text>IN</xsl:text>
							<!-- IN Buyer's item number -->
						</subelement>
						<!-- 1131   Code list qualifier (C  an..3) -->
						<!-- 3055   Code list responsible agency, coded (C  an..3) -->
						<subelement>
							<!-- 92 Assigned by buyer or buyer's agent -->
						</subelement>
					</element>
				</segment>
			</xsl:if>

			<xsl:if test="normalize-space(SupplierItemCode)">
				<!-- PIA Additional product id -->
				<segment tag="PIA">
					<!-- 4347  PRODUCT ID. FUNCTION QUALIFIER (M  an..3) -->
					<element>
						<xsl:text>1</xsl:text>
						<!-- 1  Additional identification -->
					</element>
					<!-- C212  ITEM NUMBER IDENTIFICATION (M) -->
					<element>
						<!-- 7140   Item number (C  an..35) -->
						<subelement>
							<xsl:value-of select="normalize-space(SupplierItemCode)"/>
						</subelement>
						<!-- 7143   Item number type, coded (C  an..3) -->
						<subelement>
							<xsl:text>SA</xsl:text>
							<!-- SA Supplier's article number -->
						</subelement>
						<!-- 1131   Code list qualifier (C  an..3) -->
						<!-- 3055   Code list responsible agency, coded (C  an..3) -->
						<subelement>
							<!-- 91 Assigned by seller or seller's agent -->
						</subelement>
					</element>
				</segment>
			</xsl:if>

			<segment tag="IMD">
				<element>
					<subelement>
						<xsl:text>A</xsl:text>
					</subelement>
				</element>
				<element/>
				<element>
					<subelement>
					</subelement>
					<subelement/>
					<subelement>
						<xsl:text>9</xsl:text>
					</subelement>
					<subelement>
						<!--additional specification-->
						<xsl:value-of select="normalize-space(ItemDescription)"/>
					</subelement>
				</element>
			</segment>
			<segment tag="QTY">
				<!-- C186  QUANTITY DETAILS (M) -->
				<element>
					<!-- 6063   Quantity qualifier (M  an..3) -->
					<subelement>
						<xsl:text>47</xsl:text>
						<!-- 59 Numbers of consumer units in the traded unit -->
					</subelement>
					<!-- 6060   Quantity (M  n..15) -->
					<subelement>
						<xsl:value-of select="format-number(InvoiceQuantity, '0.00')"/>
					</subelement>
					<!-- 6411   Measure unit qualifier (C  an..3) -->
				</element>
			</segment>

			<segment tag="MOA">
				<!-- C516  MONETARY AMOUNT (M) -->
				<element>
					<!-- 5025   Monetary amount type qualifier (M  an..3) -->
					<subelement>
						<xsl:text>203</xsl:text>
						<!-- 203 Line item amount -->
					</subelement>
					<!-- 5004   Monetary amount (C  n..18) -->
					<subelement>
						<xsl:value-of select="format-number(NetAmount, '0.00')"/>
					</subelement>
					<!-- 6345   Currency, coded (C  an..3) -->
					<subelement/>
					<!-- 6343   Currency qualifier (C  an..3) -->
					<subelement/>
					<!-- 4405   Status, coded (C  an..3) -->
					<subelement/>
				</element>
			</segment>
			<segment tag="MOA">
				<!-- C516  MONETARY AMOUNT (M) -->
				<element>
					<!-- 5025   Monetary amount type qualifier (M  an..3) -->
					<subelement>
						<xsl:text>131</xsl:text>
						<!-- 203 Line item amount -->
					</subelement>
					<!-- 5004   Monetary amount (C  n..18) -->
					<subelement>
						<xsl:value-of select="'0'"/>
					</subelement>
					<!-- 6345   Currency, coded (C  an..3) -->
					<subelement/>
					<!-- 6343   Currency qualifier (C  an..3) -->
					<subelement/>
					<!-- 4405   Status, coded (C  an..3) -->
					<subelement/>
				</element>
			</segment>



			<!-- Segment group 28:PRI-APR-RNG-DTM -->
			<!-- PRI Price details -->
			<segment tag="PRI">
				<!-- C509  PRICE INFORMATION (C) -->
				<element>
					<!-- 5125   Price qualifier (M  an..3) -->
					<subelement>
						<!-- AAB  	Calculation gross -->
						<xsl:text>AAB</xsl:text>
					</subelement>
					<!-- 5118   Price (C  n..15) -->
					<subelement>
						<xsl:value-of select="format-number((InvoiceUnitNetPrice+//Line-Item/TaxAmount), '0.00')"/>
					</subelement>
					<!-- 5375   Price type, coded (C  an..3) -->
					<!--subelement>
					<xsl:text>TU</xsl:text-->
					<!-- TU Traded unit -->
					<!--/subelement-->
					<!-- 5387   Price type qualifier (C  an..3) -->
					<!--subelement/-->
				</element>
			</segment>
		</xsl:if>

	</xsl:template>
	<!-- Format and change unit of measure  -->
	<xsl:template name="format_uom">
		<xsl:param name="uom"/>
		<xsl:if test="string($uom)">
			<xsl:choose>
				<xsl:when test="($uom = 'pudel') or ($uom = 'purk') or ($uom = 'tk')">
					<xsl:text>PCE</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="substring($uom, 1, 3)"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:if>
	</xsl:template>
</xsl:stylesheet><!-- Stylus Studio meta-information - (c) 2004-2009. Progress Software Corporation. All rights reserved.

<metaInformation>
	<scenarios>
		<scenario default="yes" name="Scenario1" userelativepaths="yes" externalpreview="no" url="..\..\Downloads\standard_INVOICE_DS041624 (3).xml" htmlbaseurl="" outputurl="" processortype="saxon8" useresolver="yes" profilemode="0" profiledepth=""
		          profilelength="" urlprofilexml="" commandline="" additionalpath="" additionalclasspath="" postprocessortype="none" postprocesscommandline="" postprocessadditionalpath="" postprocessgeneratedext="" validateoutput="no" validator="internal"
		          customvalidator="">
			<advancedProp name="sInitialMode" value=""/>
			<advancedProp name="bXsltOneIsOkay" value="true"/>
			<advancedProp name="bSchemaAware" value="true"/>
			<advancedProp name="bGenerateByteCode" value="true"/>
			<advancedProp name="bXml11" value="false"/>
			<advancedProp name="iValidation" value="0"/>
			<advancedProp name="bExtensions" value="true"/>
			<advancedProp name="iWhitespace" value="0"/>
			<advancedProp name="sInitialTemplate" value=""/>
			<advancedProp name="bTinyTree" value="true"/>
			<advancedProp name="xsltVersion" value="2.0"/>
			<advancedProp name="bWarnings" value="true"/>
			<advancedProp name="bUseDTD" value="false"/>
			<advancedProp name="iErrorHandling" value="fatal"/>
		</scenario>
	</scenarios>
	<MapperMetaTag>
		<MapperInfo srcSchemaPathIsRelative="yes" srcSchemaInterpretAsXML="no" destSchemaPath="" destSchemaRoot="" destSchemaPathIsRelative="yes" destSchemaInterpretAsXML="no"/>
		<MapperBlockPosition></MapperBlockPosition>
		<TemplateContext></TemplateContext>
		<MapperFilter side="source"></MapperFilter>
	</MapperMetaTag>
</metaInformation>
-->