resource "aws_instance" "example" {
  ami           = "ami-123456"
  instance_type = "t3.large"

  tags = {
    Name = "bad-instance"
  }
}

resource "aws_security_group" "open_sg" {
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
